from src.models.scheduled_transaction import SCHEDULED_TRANSACTION_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import dollars_to_milliunits, serialize, serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_scheduled_transactions(plan_id: str) -> str:
    """List all scheduled (recurring) transactions.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    transactions = await _shared.cache.get_scheduled_transactions(plan_id)
    return serialize_list(transactions, exclude=SCHEDULED_TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_scheduled_transaction(
    scheduled_transaction_id: str, plan_id: str
) -> str:
    """Get a single scheduled transaction.

    Args:
        scheduled_transaction_id: The scheduled transaction ID
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    txn = await _shared.cache.get_scheduled_transaction(scheduled_transaction_id, plan_id)
    return serialize(txn, exclude=SCHEDULED_TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def create_scheduled_transaction(
    plan_id: str,
    account_id: str,
    date: str,
    amount: float | None = None,
    payee_id: str | None = None,
    payee_name: str | None = None,
    category_id: str | None = None,
    memo: str | None = None,
    flag_color: str | None = None,
    frequency: str | None = None,
) -> str:
    """Create a scheduled transaction (a transaction with a future date).

    Splits are not supported on this endpoint. Date must be in the future, no more
    than 5 years out.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
        account_id: The account ID for this scheduled transaction
        date: Future date in YYYY-MM-DD format (no more than 5 years out)
        amount: Amount in dollars (negative for outflow, positive for inflow). e.g. -50.25 for spending $50.25
        payee_id: Payee ID (use list_payees to find available IDs). For account transfers, use the target account's transfer_payee_id.
        payee_name: Payee name. If payee_id is null, this resolves to an existing payee or creates a new one.
        category_id: Category ID. Credit Card Payment categories are not permitted.
        memo: Memo/note (max 500 chars)
        flag_color: 'red', 'orange', 'yellow', 'green', 'blue', 'purple', or null
        frequency: One of 'never', 'daily', 'weekly', 'everyOtherWeek', 'twiceAMonth',
            'every4Weeks', 'monthly', 'everyOtherMonth', 'every3Months', 'every4Months',
            'twiceAYear', 'yearly', 'everyOtherYear'
    """
    scheduled: dict = {
        "account_id": account_id,
        "date": date,
    }
    if amount is not None:
        scheduled["amount"] = dollars_to_milliunits(amount)
    if payee_id is not None:
        scheduled["payee_id"] = payee_id
    if payee_name is not None:
        scheduled["payee_name"] = payee_name
    if category_id is not None:
        scheduled["category_id"] = category_id
    if memo is not None:
        scheduled["memo"] = memo
    if flag_color is not None:
        scheduled["flag_color"] = flag_color
    if frequency is not None:
        scheduled["frequency"] = frequency

    txn = await _shared.cache.create_scheduled_transaction(scheduled, plan_id)
    return serialize(txn, exclude=SCHEDULED_TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def update_scheduled_transaction(
    plan_id: str,
    scheduled_transaction_id: str,
    account_id: str,
    date: str,
    amount: float | None = None,
    payee_id: str | None = None,
    payee_name: str | None = None,
    category_id: str | None = None,
    memo: str | None = None,
    flag_color: str | None = None,
    frequency: str | None = None,
) -> str:
    """Update a scheduled transaction.

    The API requires account_id and date on every update. Splits are not supported on
    this endpoint. Date must be in the future, no more than 5 years out.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
        scheduled_transaction_id: The scheduled transaction ID to update
        account_id: The account ID for this scheduled transaction (required)
        date: Future date in YYYY-MM-DD format (required, no more than 5 years out)
        amount: Amount in dollars (negative for outflow, positive for inflow)
        payee_id: Payee ID. For account transfers, use the target account's transfer_payee_id.
        payee_name: Payee name (resolves to existing or creates a new payee)
        category_id: Category ID. Credit Card Payment categories are not permitted.
        memo: Memo/note (max 500 chars)
        flag_color: 'red', 'orange', 'yellow', 'green', 'blue', 'purple', or null
        frequency: One of 'never', 'daily', 'weekly', 'everyOtherWeek', 'twiceAMonth',
            'every4Weeks', 'monthly', 'everyOtherMonth', 'every3Months', 'every4Months',
            'twiceAYear', 'yearly', 'everyOtherYear'
    """
    scheduled: dict = {
        "account_id": account_id,
        "date": date,
    }
    if amount is not None:
        scheduled["amount"] = dollars_to_milliunits(amount)
    if payee_id is not None:
        scheduled["payee_id"] = payee_id
    if payee_name is not None:
        scheduled["payee_name"] = payee_name
    if category_id is not None:
        scheduled["category_id"] = category_id
    if memo is not None:
        scheduled["memo"] = memo
    if flag_color is not None:
        scheduled["flag_color"] = flag_color
    if frequency is not None:
        scheduled["frequency"] = frequency

    txn = await _shared.cache.update_scheduled_transaction(
        scheduled_transaction_id, scheduled, plan_id
    )
    return serialize(txn, exclude=SCHEDULED_TRANSACTION_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def delete_scheduled_transaction(
    scheduled_transaction_id: str, plan_id: str
) -> str:
    """Delete a scheduled transaction.

    Args:
        scheduled_transaction_id: The scheduled transaction ID to delete
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    txn = await _shared.cache.delete_scheduled_transaction(scheduled_transaction_id, plan_id)
    return serialize(txn, exclude=SCHEDULED_TRANSACTION_DISPLAY_EXCLUDE)
