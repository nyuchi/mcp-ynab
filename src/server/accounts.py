from src.models.account import ACCOUNT_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import serialize, serialize_list


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
async def get_account(account_id: str, plan_id: str) -> str:
    """Get details for a specific account.

    Args:
        account_id: The account ID
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    account = await _shared.cache.get_account(account_id, plan_id)
    return serialize(account, exclude=ACCOUNT_DISPLAY_EXCLUDE)
