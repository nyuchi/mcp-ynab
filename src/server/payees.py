from src.models.payee import PAYEE_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_payees(budget_id: str) -> str:
    """List all payees in a budget.

    Args:
        budget_id: The budget ID (use list_budgets to find available IDs)
    """
    payees = await _shared.cache.get_payees(budget_id)
    return serialize_list(payees, exclude=PAYEE_DISPLAY_EXCLUDE)
