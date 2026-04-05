from __future__ import annotations

from pydantic import Field

from src.models.account import Account
from src.models.category import Category, CategoryGroup
from src.models.common import YNABBaseModel
from src.models.month import MonthDetail
from src.models.payee import Payee
from src.models.payee_location import PayeeLocation
from src.models.transaction import ScheduledTransaction, Subtransaction, Transaction

PLAN_SUMMARY_DISPLAY_EXCLUDE: set[str] = set()


class DateFormat(YNABBaseModel):
    format: str = Field()


class CurrencyFormat(YNABBaseModel):
    iso_code: str = Field()
    example_format: str = Field()
    decimal_digits: int = Field()
    decimal_separator: str = Field()
    symbol_first: bool = Field()
    group_separator: str = Field()
    currency_symbol: str = Field()
    display_symbol: bool = Field()


class ScheduledSubtransaction(YNABBaseModel):
    id: str = Field()
    scheduled_transaction_id: str = Field()
    amount: int = Field(default=0)
    memo: str | None = Field(default=None)
    payee_id: str | None = Field(default=None)
    payee_name: str | None = Field(default=None)
    category_id: str | None = Field(default=None)
    category_name: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None)
    transfer_transaction_id: str | None = Field(default=None)
    deleted: bool = Field(default=False)


class PlanSettings(YNABBaseModel):
    date_format: DateFormat | None = Field(default=None)
    currency_format: CurrencyFormat | None = Field(default=None)


class PlanSummary(YNABBaseModel):
    id: str = Field()
    name: str = Field()
    last_modified_on: str | None = Field(default=None)
    first_month: str | None = Field(default=None)
    last_month: str | None = Field(default=None)
    date_format: DateFormat | None = Field(default=None)
    currency_format: CurrencyFormat | None = Field(default=None)
    accounts: list[Account] | None = Field(default=None)


class PlanDetail(YNABBaseModel):
    id: str = Field()
    name: str = Field()
    last_modified_on: str | None = Field(default=None)
    first_month: str | None = Field(default=None)
    last_month: str | None = Field(default=None)
    date_format: DateFormat | None = Field(default=None)
    currency_format: CurrencyFormat | None = Field(default=None)
    accounts: list[Account] = Field(default=[])
    payees: list[Payee] = Field(default=[])
    payee_locations: list[PayeeLocation] = Field(default=[])
    category_groups: list[CategoryGroup] = Field(default=[])
    categories: list[Category] = Field(default=[])
    months: list[MonthDetail] = Field(default=[])
    transactions: list[Transaction] = Field(default=[])
    subtransactions: list[Subtransaction] = Field(default=[])
    scheduled_transactions: list[ScheduledTransaction] = Field(default=[])
    scheduled_subtransactions: list[ScheduledSubtransaction] = Field(default=[])
