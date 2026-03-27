import json

from src.models.transaction import TRANSACTION_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import dollars_to_milliunits, serialize, serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_transactions(
    plan_id: str,
    since_date: str | None = None,
    type: str | None = None,
) -> str:
    """List transactions in a plan. Can filter by date and type.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
        since_date: Only return transactions on or after this date (YYYY-MM-DD)
        type: Filter by 'uncategorized' or 'unapproved'
    """
    transactions = await _shared.cache.get_transactions(plan_id, since_date, type)
    return serialize_list(transactions, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_transaction(transaction_id: str, plan_id: str) -> str:
    """Get a specific transaction by ID.

    Args:
        transaction_id: The transaction ID
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    txn = await _shared.cache.get_transaction(transaction_id, plan_id)
    return serialize(txn, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_transactions_by_account(
    account_id: str,
    plan_id: str,
    since_date: str | None = None,
) -> str:
    """Get transactions for a specific account.

    Args:
        account_id: The account ID
        plan_id: The plan ID (use list_plans to find available IDs)
        since_date: Only return transactions on or after this date (YYYY-MM-DD)
    """
    transactions = await _shared.cache.get_transactions_by_account(account_id, plan_id, since_date)
    return serialize_list(transactions, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_transactions_by_category(
    category_id: str,
    plan_id: str,
    since_date: str | None = None,
) -> str:
    """Get transactions for a specific category.

    Args:
        category_id: The category ID
        plan_id: The plan ID (use list_plans to find available IDs)
        since_date: Only return transactions on or after this date (YYYY-MM-DD)
    """
    transactions = await _shared.cache.get_transactions_by_category(category_id, plan_id, since_date)
    return serialize_list(transactions, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_transactions_by_payee(
    payee_id: str,
    plan_id: str,
    since_date: str | None = None,
) -> str:
    """Get transactions for a specific payee.

    Args:
        payee_id: The payee ID
        plan_id: The plan ID (use list_plans to find available IDs)
        since_date: Only return transactions on or after this date (YYYY-MM-DD)
    """
    transactions = await _shared.cache.get_transactions_by_payee(payee_id, plan_id, since_date)
    return serialize_list(transactions, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def search_transactions(
    plan_id: str,
    query: str,
    since_date: str | None = None,
    amount_min: float | None = None,
    amount_max: float | None = None,
) -> str:
    """Search transactions by text across payee, memo, and category fields.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
        query: Text to search for (case-insensitive, matches payee, memo, and category)
        since_date: Only search transactions on or after this date (YYYY-MM-DD)
        amount_min: Minimum amount in dollars (e.g. -100.00). Filters by absolute value if both min and max are positive, otherwise by raw value.
        amount_max: Maximum amount in dollars (e.g. -10.00)
    """
    transactions = await _shared.cache.get_transactions(plan_id, since_date)
    q = query.lower()

    matches = []
    for t in transactions:
        fields = [t.payee_name or "", t.memo or "", t.category_name or ""]
        if not any(q in f.lower() for f in fields):
            continue

        if amount_min is not None and t.amount < dollars_to_milliunits(amount_min):
            continue
        if amount_max is not None and t.amount > dollars_to_milliunits(amount_max):
            continue

        matches.append(t)

    return serialize_list(matches, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def create_transaction(
    plan_id: str,
    account_id: str,
    date: str,
    amount: float,
    payee_name: str | None = None,
    category_id: str | None = None,
    memo: str | None = None,
    cleared: str = "uncleared",
    approved: bool = False,
) -> str:
    """Create a new transaction.

    Args:
        account_id: The account ID for this transaction
        date: Transaction date in YYYY-MM-DD format
        amount: Amount in dollars (negative for outflow, positive for inflow). e.g. -50.25 for spending $50.25
        payee_name: Name of the payee
        category_id: Category ID to assign
        memo: Optional memo/note
        cleared: 'cleared', 'uncleared', or 'reconciled'
        approved: Whether the transaction is approved
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    transaction = {
        "account_id": account_id,
        "date": date,
        "amount": dollars_to_milliunits(amount),
        "cleared": cleared,
        "approved": approved,
    }
    if payee_name:
        transaction["payee_name"] = payee_name
    if category_id:
        transaction["category_id"] = category_id
    if memo:
        transaction["memo"] = memo

    txn = await _shared.cache.create_transaction(transaction, plan_id)
    return serialize(txn, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def create_transactions(
    plan_id: str,
    account_id: str,
    transactions: list[dict],
) -> str:
    """Create multiple transactions in a single API call. Ideal for bulk imports.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
        account_id: Default account ID for all transactions
        transactions: List of transaction dicts, each with:
            - date: Transaction date in YYYY-MM-DD format
            - amount: Amount in dollars (negative for outflow, positive for inflow)
            - payee_name: (optional) Name of the payee
            - category_id: (optional) Category ID to assign
            - memo: (optional) Memo/note
            - account_id: (optional) Override the default account ID
            - cleared: (optional) 'cleared', 'uncleared', or 'reconciled' (default: 'uncleared')
            - approved: (optional) Whether the transaction is approved (default: false)
    """
    prepared = []
    for txn_input in transactions:
        txn = {
            "account_id": txn_input.get("account_id", account_id),
            "date": txn_input["date"],
            "amount": dollars_to_milliunits(txn_input["amount"]),
            "cleared": txn_input.get("cleared", "uncleared"),
            "approved": txn_input.get("approved", False),
        }
        if txn_input.get("payee_name"):
            txn["payee_name"] = txn_input["payee_name"]
        if txn_input.get("category_id"):
            txn["category_id"] = txn_input["category_id"]
        if txn_input.get("memo"):
            txn["memo"] = txn_input["memo"]
        prepared.append(txn)

    txns = await _shared.cache.create_transactions(prepared, plan_id)
    return serialize_list(txns, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def update_transaction(
    plan_id: str,
    transaction_id: str,
    account_id: str | None = None,
    date: str | None = None,
    amount: float | None = None,
    payee_name: str | None = None,
    category_id: str | None = None,
    memo: str | None = None,
    cleared: str | None = None,
    approved: bool | None = None,
) -> str:
    """Update an existing transaction. Only provide the fields you want to change.

    Args:
        transaction_id: The transaction ID to update
        account_id: New account ID
        date: New date (YYYY-MM-DD)
        amount: New amount in dollars (negative for outflow, positive for inflow)
        payee_name: New payee name
        category_id: New category ID
        memo: New memo
        cleared: 'cleared', 'uncleared', or 'reconciled'
        approved: Whether the transaction is approved
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    transaction = {}
    if account_id is not None:
        transaction["account_id"] = account_id
    if date is not None:
        transaction["date"] = date
    if amount is not None:
        transaction["amount"] = dollars_to_milliunits(amount)
    if payee_name is not None:
        transaction["payee_name"] = payee_name
    if category_id is not None:
        transaction["category_id"] = category_id
    if memo is not None:
        transaction["memo"] = memo
    if cleared is not None:
        transaction["cleared"] = cleared
    if approved is not None:
        transaction["approved"] = approved

    txn = await _shared.cache.update_transaction(transaction_id, transaction, plan_id)
    return serialize(txn, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def delete_transaction(transaction_id: str, plan_id: str) -> str:
    """Delete a transaction.

    Args:
        transaction_id: The transaction ID to delete
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    txn = await _shared.cache.delete_transaction(transaction_id, plan_id)
    return serialize(txn, exclude=TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def update_transactions(
    plan_id: str,
    transactions: list[dict],
) -> str:
    """Update multiple transactions in a single API call. Each transaction must include its ID.

    Only provided fields are updated (sparse update). Ideal for bulk recategorization,
    bulk approval, bulk clearing, etc.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
        transactions: List of transaction dicts, each requiring:
            - id: The transaction ID to update
            And optionally:
            - account_id: New account ID
            - date: New date (YYYY-MM-DD)
            - amount: New amount in dollars (negative for outflow, positive for inflow)
            - payee_name: New payee name
            - category_id: New category ID
            - memo: New memo
            - cleared: 'cleared', 'uncleared', or 'reconciled'
            - approved: Whether the transaction is approved
            - flag_color: Flag color ('red', 'orange', 'yellow', 'green', 'blue', 'purple', or null)
    """
    prepared = []
    for txn_input in transactions:
        if "id" not in txn_input:
            return json.dumps({"error": "Each transaction must include an 'id' field"})
        txn: dict = {"id": txn_input["id"]}
        if "account_id" in txn_input:
            txn["account_id"] = txn_input["account_id"]
        if "date" in txn_input:
            txn["date"] = txn_input["date"]
        if "amount" in txn_input:
            txn["amount"] = dollars_to_milliunits(txn_input["amount"])
        if "payee_name" in txn_input:
            txn["payee_name"] = txn_input["payee_name"]
        if "category_id" in txn_input:
            txn["category_id"] = txn_input["category_id"]
        if "memo" in txn_input:
            txn["memo"] = txn_input["memo"]
        if "cleared" in txn_input:
            txn["cleared"] = txn_input["cleared"]
        if "approved" in txn_input:
            txn["approved"] = txn_input["approved"]
        if "flag_color" in txn_input:
            txn["flag_color"] = txn_input["flag_color"]
        prepared.append(txn)

    txns = await _shared.cache.update_transactions(prepared, plan_id)
    return serialize_list(txns, exclude=TRANSACTION_DISPLAY_EXCLUDE)
