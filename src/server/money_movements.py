from src.server import _shared
from src.server._shared import serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_money_movements(plan_id: str) -> str:
    """List all money movements in a plan.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    movements = await _shared.cache.get_money_movements(plan_id)
    return serialize_list(movements)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_money_movements_for_month(month: str, plan_id: str) -> str:
    """Get all money movements for a specific month.

    Args:
        month: Month in YYYY-MM-DD format (first of month) or 'current'
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    movements = await _shared.cache.get_money_movements_for_month(month, plan_id)
    return serialize_list(movements)


@_shared.mcp.tool()
@_shared.handle_errors
async def list_money_movement_groups(plan_id: str) -> str:
    """List all money movement groups in a plan.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    groups = await _shared.cache.get_money_movement_groups(plan_id)
    return serialize_list(groups)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_money_movement_groups_for_month(month: str, plan_id: str) -> str:
    """Get all money movement groups for a specific month.

    Args:
        month: Month in YYYY-MM-DD format (first of month) or 'current'
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    groups = await _shared.cache.get_money_movement_groups_for_month(month, plan_id)
    return serialize_list(groups)
