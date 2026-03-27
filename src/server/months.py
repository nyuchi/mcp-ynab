import json

from src.models.month import MONTH_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_months(budget_id: str) -> str:
    """List all budget months.

    Args:
        budget_id: The budget ID (use list_budgets to find available IDs)
    """
    months = await _shared.cache.get_months(budget_id)
    return serialize_list(months, exclude=MONTH_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_month(month: str, budget_id: str) -> str:
    """Get detailed budget month summary including all categories. Use 'current' for the current month.

    Args:
        month: Month in YYYY-MM-DD format (first of month) or 'current'
        budget_id: The budget ID (use list_budgets to find available IDs)
    """
    m = await _shared.cache.get_month(month, budget_id)
    md = m.model_dump(by_alias=True, exclude=MONTH_DISPLAY_EXCLUDE)
    md["categories"] = [
        c.model_dump(by_alias=True)
        for c in m.categories
    ]
    return json.dumps(md, indent=2)
