from src.models.payee import PAYEE_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_payees(plan_id: str) -> str:
    """List all payees in a plan.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    payees = await _shared.cache.get_payees(plan_id)
    return serialize_list(payees, exclude=PAYEE_DISPLAY_EXCLUDE)
