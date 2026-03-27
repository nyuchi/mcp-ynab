from src.models.account import ACCOUNT_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import serialize, serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_accounts(budget_id: str) -> str:
    """List all accounts in a budget.

    Args:
        budget_id: The budget ID (use list_budgets to find available IDs)
    """
    accounts = await _shared.cache.get_accounts(budget_id)
    return serialize_list(accounts, exclude=ACCOUNT_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_account(account_id: str, budget_id: str) -> str:
    """Get details for a specific account.

    Args:
        account_id: The account ID
        budget_id: The budget ID (use list_budgets to find available IDs)
    """
    account = await _shared.cache.get_account(account_id, budget_id)
    return serialize(account, exclude=ACCOUNT_DISPLAY_EXCLUDE)
