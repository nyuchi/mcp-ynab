import json

from src.models.month import MONTH_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_months(plan_id: str) -> str:
    """List all plan months.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    months = await _shared.cache.get_months(plan_id)
    return serialize_list(months, exclude=MONTH_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_month(month: str, plan_id: str) -> str:
    """Get detailed plan month summary including all categories. Use 'current' for the current month.

    Args:
        month: Month in YYYY-MM-DD format (first of month) or 'current'
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    m = await _shared.cache.get_month(month, plan_id)
    md = m.model_dump(by_alias=True, exclude=MONTH_DISPLAY_EXCLUDE)
    md["categories"] = [
        c.model_dump(by_alias=True)
        for c in m.categories
    ]
    return json.dumps(md, indent=2)
