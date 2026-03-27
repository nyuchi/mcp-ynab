from src.models.plan import PLAN_SUMMARY_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import serialize, serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_plans() -> str:
    """List all plans in the user's YNAB account. Call this first to get plan IDs."""
    plans = await _shared.cache.get_plans()
    return serialize_list(plans, exclude=PLAN_SUMMARY_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_plan(plan_id: str) -> str:
    """Get details for a specific plan.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    plan = await _shared.cache.get_plan(plan_id)
    return serialize(plan)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_plan_settings(plan_id: str) -> str:
    """Get settings for a plan (date format and currency format).

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    settings = await _shared.cache.get_plan_settings(plan_id)
    return serialize(settings)
