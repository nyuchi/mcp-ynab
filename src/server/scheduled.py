from src.models.transaction import SCHEDULED_TRANSACTION_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_scheduled_transactions(plan_id: str) -> str:
    """List all scheduled (recurring) transactions.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    transactions = await _shared.cache.get_scheduled_transactions(plan_id)
    return serialize_list(transactions, exclude=SCHEDULED_TRANSACTION_DISPLAY_EXCLUDE)
