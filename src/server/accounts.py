from src.models.account import ACCOUNT_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import dollars_to_milliunits, serialize, serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_accounts(plan_id: str) -> str:
    """List all accounts in a plan.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    accounts = await _shared.cache.get_accounts(plan_id)
    return serialize_list(accounts, exclude=ACCOUNT_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def create_account(
    plan_id: str,
    name: str,
    type: str,
    balance: float,
) -> str:
    """Create a new account.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
        name: The name of the account
        type: The type of account ('checking', 'savings', 'cash', 'creditCard', 'lineOfCredit', 'otherAsset', 'otherLiability', 'mortgage', 'autoLoan', 'studentLoan', 'personalLoan', 'medicalDebt', 'otherDebt')
        balance: The current balance in dollars (e.g. 1000.00)
    """
    account = {
        "name": name,
        "type": type,
        "balance": dollars_to_milliunits(balance),
    }
    acct = await _shared.cache.create_account(account, plan_id)
    return serialize(acct)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_account(account_id: str, plan_id: str) -> str:
    """Get details for a specific account.

    Args:
        account_id: The account ID
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    account = await _shared.cache.get_account(account_id, plan_id)
    return serialize(account, exclude=ACCOUNT_DISPLAY_EXCLUDE)
