import logging
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import TypeVar

from sqlalchemy import select

from src.cache.delta import DeltaSyncManager
from src.cache.fallback import RetryWithFallback
from src.config import Settings
from src.db.engine import get_session
from src.db.tables import ResponseCache
from src.models import (
    Account,
    PlanDetail,
    PlanSettings,
    PlanSummary,
    Category,
    CategoryGroup,
    MonthDetail,
    MonthSummary,
    Payee,
    ScheduledTransaction,
    Transaction,
    User,
)
from src.models.common import YNABBaseModel
from src.ynab_client import YNABClient

T = TypeVar("T", bound=YNABBaseModel)

logger = logging.getLogger(__name__)

# Delta sync endpoint keys (used for server_knowledge tracking and invalidation)
ENDPOINT_ACCOUNTS = "accounts"
ENDPOINT_TRANSACTIONS = "transactions"
ENDPOINT_CATEGORIES = "categories"
ENDPOINT_PAYEES = "payees"
ENDPOINT_MONTHS = "months"

# Delta sync entity type keys (used for entity storage)
ENTITY_ACCOUNT = "account"
ENTITY_TRANSACTION = "transaction"
ENTITY_CATEGORY = "category"
ENTITY_CATEGORY_GROUP = "category_group"
ENTITY_PAYEE = "payee"
ENTITY_MONTH = "month"


class CacheService:
    def __init__(self, client: YNABClient, settings: Settings):
        self.client = client
        self.settings = settings
        self.delta = DeltaSyncManager(min_interval=settings.delta_min_interval)
        self.retry = RetryWithFallback(
            max_attempts=settings.retry_max_attempts,
            base_delay=settings.retry_base_delay,
            max_delay=settings.retry_max_delay,
        )

    # ── TTL Cache helpers ────────────────────────────────────

    async def _get_cached_model(
        self, cache_key: str, ttl: int, model_class: type[T]
    ) -> T | None:
        async with get_session() as session:
            stmt = select(ResponseCache).where(ResponseCache.cache_key == cache_key)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                return None
            elapsed = (datetime.now(timezone.utc) - row.cached_at.replace(tzinfo=timezone.utc)).total_seconds()
            if elapsed < ttl:
                return row.to_model(model_class)
            return None

    async def _get_cached_model_list(
        self, cache_key: str, ttl: int, model_class: type[T]
    ) -> list[T] | None:
        async with get_session() as session:
            stmt = select(ResponseCache).where(ResponseCache.cache_key == cache_key)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                return None
            elapsed = (datetime.now(timezone.utc) - row.cached_at.replace(tzinfo=timezone.utc)).total_seconds()
            if elapsed < ttl:
                return row.to_model_list(model_class)
            return None

    async def _set_cached_model(
        self, cache_key: str, model: YNABBaseModel, ttl: int
    ) -> None:
        async with get_session() as session:
            stmt = select(ResponseCache).where(ResponseCache.cache_key == cache_key)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            if row:
                row.update_from_model(model)
            else:
                session.add(ResponseCache.from_model(cache_key, model, ttl))
            await session.commit()

    async def _set_cached_model_list(
        self, cache_key: str, models: Sequence[YNABBaseModel], ttl: int
    ) -> None:
        async with get_session() as session:
            stmt = select(ResponseCache).where(ResponseCache.cache_key == cache_key)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            if row:
                row.update_from_model_list(models)
            else:
                session.add(ResponseCache.from_model_list(cache_key, models, ttl))
            await session.commit()

    # ── Delta sync helpers ───────────────────────────────────

    async def _delta_sync(
        self,
        plan_id: str,
        endpoint: str,
        entity_type: str,
        model_class: type[T],
        fetch_fn,
    ) -> list[T]:
        if await self.delta.should_sync(plan_id, endpoint):
            knowledge = await self.delta.get_knowledge(plan_id, endpoint)

            async def api_call():
                return await fetch_fn(plan_id, last_knowledge_of_server=knowledge)

            cache_key = f"delta:{plan_id}:{endpoint}"
            try:
                entities, new_knowledge = await self.retry.execute(api_call, cache_key=cache_key)
                await self.delta.upsert_entities(plan_id, entity_type, entities)
                await self.delta.update_knowledge(plan_id, endpoint, new_knowledge)
            except Exception:
                if await self.delta.has_cached_data(plan_id, endpoint):
                    logger.warning(f"Delta sync failed for {endpoint}, using cached data")
                else:
                    raise

        return await self.delta.get_cached_entities(plan_id, entity_type, model_class)

    async def _delta_sync_categories(self, plan_id: str) -> None:
        """Sync both category groups and categories via delta."""
        endpoint = ENDPOINT_CATEGORIES
        if not await self.delta.should_sync(plan_id, endpoint):
            return

        knowledge = await self.delta.get_knowledge(plan_id, endpoint)

        async def api_call():
            return await self.client.get_categories(plan_id, last_knowledge_of_server=knowledge)

        cache_key = f"delta:{plan_id}:{endpoint}"
        try:
            groups, new_knowledge = await self.retry.execute(api_call, cache_key=cache_key)

            # Flatten: store groups (without categories) and categories separately
            flat_groups: list[YNABBaseModel] = []
            flat_cats: list[YNABBaseModel] = []
            for group in groups:
                flat_cats.extend(group.categories)
                # Store group without nested categories to avoid duplication
                flat_groups.append(CategoryGroup(
                    id=group.id, name=group.name, hidden=group.hidden,
                    deleted=group.deleted, categories=[],
                ))

            await self.delta.upsert_entities(plan_id, ENTITY_CATEGORY_GROUP, flat_groups)
            await self.delta.upsert_entities(plan_id, ENTITY_CATEGORY, flat_cats)
            await self.delta.update_knowledge(plan_id, endpoint, new_knowledge)
        except Exception:
            if await self.delta.has_cached_data(plan_id, endpoint):
                logger.warning("Category delta sync failed, using cached data")
            else:
                raise

    # ── Public API ───────────────────────────────────────────

    # User (TTL cached)

    async def get_user(self) -> User:
        cache_key = "user"
        ttl = self.settings.ttl_budgets
        cached = await self._get_cached_model(cache_key, ttl, User)
        if cached is not None:
            return cached

        user = await self.retry.execute(
            self.client.get_user, cache_key=cache_key,
        )
        await self._set_cached_model(cache_key, user, ttl)
        return user

    # Budgets (TTL cached, no delta)

    async def get_plans(self) -> list[PlanSummary]:
        cache_key = "budgets"
        ttl = self.settings.ttl_budgets
        cached = await self._get_cached_model_list(cache_key, ttl, PlanSummary)
        if cached is not None:
            return cached

        budgets = await self.retry.execute(
            self.client.get_plans, cache_key=cache_key,
        )
        await self._set_cached_model_list(cache_key, budgets, ttl)
        return budgets

    async def get_plan_settings(self, plan_id: str) -> PlanSettings:
        cache_key = f"plan_settings:{plan_id}"
        ttl = self.settings.ttl_budgets
        cached = await self._get_cached_model(cache_key, ttl, PlanSettings)
        if cached is not None:
            return cached

        settings = await self.retry.execute(
            lambda: self.client.get_plan_settings(plan_id), cache_key=cache_key,
        )
        await self._set_cached_model(cache_key, settings, ttl)
        return settings

    async def get_plan(self, plan_id: str) -> PlanDetail:
        cache_key = f"budget:{plan_id}"
        ttl = self.settings.ttl_budgets
        cached = await self._get_cached_model(cache_key, ttl, PlanDetail)
        if cached is not None:
            return cached

        budget = await self.retry.execute(
            lambda: self.client.get_plan(plan_id), cache_key=cache_key,
        )
        await self._set_cached_model(cache_key, budget, ttl)
        return budget

    # Accounts (delta synced)

    async def get_accounts(self, plan_id: str) -> list[Account]:
        return await self._delta_sync(
            plan_id, ENDPOINT_ACCOUNTS, ENTITY_ACCOUNT, Account,
            lambda bid, **kw: self.client.get_accounts(bid, **kw),
        )

    async def create_account(self, account: dict, plan_id: str) -> Account:
        acct = await self.client.create_account(account, plan_id)
        await self.delta.invalidate_knowledge(plan_id, ENDPOINT_ACCOUNTS)
        return acct

    async def get_account(self, account_id: str, plan_id: str) -> Account:
        accounts = await self.get_accounts(plan_id)
        for a in accounts:
            if a.id == account_id:
                return a
        # Fallback to direct API
        cache_key = f"account:{plan_id}:{account_id}"
        cached = await self._get_cached_model(cache_key, self.settings.ttl_single_entity, Account)
        if cached is not None:
            return cached

        account = await self.retry.execute(
            lambda: self.client.get_account(account_id, plan_id), cache_key=cache_key,
        )
        await self._set_cached_model(cache_key, account, self.settings.ttl_single_entity)
        return account

    # Transactions (delta synced)

    async def _sync_transactions(self, plan_id: str) -> list[Transaction]:
        return await self._delta_sync(
            plan_id, ENDPOINT_TRANSACTIONS, ENTITY_TRANSACTION, Transaction,
            lambda bid, **kw: self.client.get_transactions(bid, **kw),
        )

    async def get_transactions(
        self,
        plan_id: str,
        since_date: str | None = None,
        type: str | None = None,
    ) -> list[Transaction]:
        txns = await self._sync_transactions(plan_id)
        if since_date:
            txns = [t for t in txns if t.date >= since_date]
        if type == "uncategorized":
            txns = [t for t in txns if not t.category_id]
        elif type == "unapproved":
            txns = [t for t in txns if not t.approved]
        return txns

    async def get_transaction(self, transaction_id: str, plan_id: str) -> Transaction:
        txns = await self._sync_transactions(plan_id)
        for t in txns:
            if t.id == transaction_id:
                return t
        # Fallback to direct API
        cache_key = f"transaction:{plan_id}:{transaction_id}"
        cached = await self._get_cached_model(cache_key, self.settings.ttl_single_entity, Transaction)
        if cached is not None:
            return cached

        txn = await self.retry.execute(
            lambda: self.client.get_transaction(transaction_id, plan_id), cache_key=cache_key,
        )
        await self._set_cached_model(cache_key, txn, self.settings.ttl_single_entity)
        return txn

    async def get_transactions_by_account(
        self,
        account_id: str,
        plan_id: str,
        since_date: str | None = None,
    ) -> list[Transaction]:
        txns = await self._sync_transactions(plan_id)
        txns = [t for t in txns if t.account_id == account_id]
        if since_date:
            txns = [t for t in txns if t.date >= since_date]
        return txns

    async def get_transactions_by_category(
        self,
        category_id: str,
        plan_id: str,
        since_date: str | None = None,
    ) -> list[Transaction]:
        txns = await self._sync_transactions(plan_id)
        txns = [t for t in txns if t.category_id == category_id]
        if since_date:
            txns = [t for t in txns if t.date >= since_date]
        return txns

    async def get_transactions_by_payee(
        self,
        payee_id: str,
        plan_id: str,
        since_date: str | None = None,
    ) -> list[Transaction]:
        txns = await self._sync_transactions(plan_id)
        txns = [t for t in txns if t.payee_id == payee_id]
        if since_date:
            txns = [t for t in txns if t.date >= since_date]
        return txns

    # Transaction mutations

    async def create_transaction(self, transaction: dict, plan_id: str) -> Transaction:
        txn = await self.client.create_transaction(transaction, plan_id)
        await self.delta.upsert_entities(plan_id, ENTITY_TRANSACTION, [txn])
        return txn

    async def create_transactions(
        self, transactions: list[dict], plan_id: str
    ) -> list[Transaction]:
        txns = await self.client.create_transactions(transactions, plan_id)
        await self.delta.upsert_entities(plan_id, ENTITY_TRANSACTION, txns)
        return txns

    async def update_transaction(
        self, transaction_id: str, transaction: dict, plan_id: str
    ) -> Transaction:
        txn = await self.client.update_transaction(transaction_id, transaction, plan_id)
        await self.delta.upsert_entities(plan_id, ENTITY_TRANSACTION, [txn])
        return txn

    async def update_transactions(
        self, transactions: list[dict], plan_id: str
    ) -> list[Transaction]:
        txns = await self.client.update_transactions(transactions, plan_id)
        await self.delta.upsert_entities(plan_id, ENTITY_TRANSACTION, txns)
        return txns

    async def delete_transaction(self, transaction_id: str, plan_id: str) -> Transaction:
        txn = await self.client.delete_transaction(transaction_id, plan_id)
        await self.delta.upsert_entities(plan_id, ENTITY_TRANSACTION, [txn])
        return txn

    # Categories (delta synced)

    async def get_categories(self, plan_id: str) -> list[CategoryGroup]:
        await self._delta_sync_categories(plan_id)

        groups = await self.delta.get_cached_entities(plan_id, ENTITY_CATEGORY_GROUP, CategoryGroup)
        cats = await self.delta.get_cached_entities(plan_id, ENTITY_CATEGORY, Category)

        # Reconstruct nested structure
        groups_by_id: dict[str, CategoryGroup] = {g.id: g for g in groups}
        for cat in cats:
            group = groups_by_id.get(cat.category_group_id)
            if group:
                group.categories.append(cat)

        return list(groups_by_id.values())

    async def get_category_for_month(
        self, month: str, category_id: str, plan_id: str
    ) -> Category:
        cache_key = f"category_month:{plan_id}:{month}:{category_id}"
        cached = await self._get_cached_model(cache_key, self.settings.ttl_month_detail, Category)
        if cached is not None:
            return cached

        cat = await self.retry.execute(
            lambda: self.client.get_category_for_month(month, category_id, plan_id),
            cache_key=cache_key,
        )
        await self._set_cached_model(cache_key, cat, self.settings.ttl_month_detail)
        return cat

    async def get_category(self, category_id: str, plan_id: str) -> Category:
        groups = await self.get_categories(plan_id)
        for g in groups:
            for c in g.categories:
                if c.id == category_id:
                    return c
        # Fallback to direct API
        cache_key = f"category:{plan_id}:{category_id}"
        cached = await self._get_cached_model(cache_key, self.settings.ttl_single_entity, Category)
        if cached is not None:
            return cached

        cat = await self.retry.execute(
            lambda: self.client.get_category(category_id, plan_id), cache_key=cache_key,
        )
        await self._set_cached_model(cache_key, cat, self.settings.ttl_single_entity)
        return cat

    async def create_category(self, category: dict, plan_id: str) -> Category:
        cat = await self.client.create_category(category, plan_id)
        await self.delta.invalidate_knowledge(plan_id, ENDPOINT_CATEGORIES)
        return cat

    async def update_category_group(
        self, category_group_id: str, category_group: dict, plan_id: str
    ) -> CategoryGroup:
        group = await self.client.update_category_group(category_group_id, category_group, plan_id)
        await self.delta.invalidate_knowledge(plan_id, ENDPOINT_CATEGORIES)
        return group

    async def create_category_group(
        self, category_group: dict, plan_id: str
    ) -> CategoryGroup:
        group = await self.client.create_category_group(category_group, plan_id)
        await self.delta.invalidate_knowledge(plan_id, ENDPOINT_CATEGORIES)
        return group

    async def update_category(
        self, category_id: str, category: dict, plan_id: str
    ) -> Category:
        cat = await self.client.update_category(category_id, category, plan_id)
        await self.delta.invalidate_knowledge(plan_id, ENDPOINT_CATEGORIES)
        return cat

    async def update_category_for_month(
        self, month: str, category_id: str, budgeted: int, plan_id: str
    ) -> Category:
        cat = await self.client.update_category_for_month(month, category_id, budgeted, plan_id)
        await self.delta.invalidate_knowledge(plan_id, ENDPOINT_CATEGORIES)
        await self.delta.invalidate_knowledge(plan_id, ENDPOINT_MONTHS)
        return cat

    # Payees (delta synced)

    async def get_payees(self, plan_id: str) -> list[Payee]:
        return await self._delta_sync(
            plan_id, ENDPOINT_PAYEES, ENTITY_PAYEE, Payee,
            lambda bid, **kw: self.client.get_payees(bid, **kw),
        )

    # Months (delta synced)

    async def get_months(self, plan_id: str) -> list[MonthSummary]:
        return await self._delta_sync(
            plan_id, ENDPOINT_MONTHS, ENTITY_MONTH, MonthSummary,
            lambda bid, **kw: self.client.get_months(bid, **kw),
        )

    async def get_month(self, month: str, plan_id: str) -> MonthDetail:
        cache_key = f"month_detail:{plan_id}:{month}"
        cached = await self._get_cached_model(cache_key, self.settings.ttl_month_detail, MonthDetail)
        if cached is not None:
            return cached

        m = await self.retry.execute(
            lambda: self.client.get_month(month, plan_id), cache_key=cache_key,
        )
        await self._set_cached_model(cache_key, m, self.settings.ttl_month_detail)
        return m

    # Scheduled Transactions (TTL cached)

    async def get_scheduled_transactions(self, plan_id: str) -> list[ScheduledTransaction]:
        cache_key = f"scheduled_transactions:{plan_id}"
        ttl = self.settings.ttl_scheduled_transactions
        cached = await self._get_cached_model_list(cache_key, ttl, ScheduledTransaction)
        if cached is not None:
            return cached

        txns = await self.retry.execute(
            lambda: self.client.get_scheduled_transactions(plan_id), cache_key=cache_key,
        )
        await self._set_cached_model_list(cache_key, txns, ttl)
        return txns
