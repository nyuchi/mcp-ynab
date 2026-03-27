from src.models.budget import BUDGET_SUMMARY_DISPLAY_EXCLUDE
from src.server import _shared
from src.server._shared import serialize, serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_budgets() -> str:
    """List all budgets in the user's YNAB account. Call this first to get budget IDs."""
    budgets = await _shared.cache.get_budgets()
    return serialize_list(budgets, exclude=BUDGET_SUMMARY_DISPLAY_EXCLUDE)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_budget(budget_id: str) -> str:
    """Get details for a specific budget.

    Args:
        budget_id: The budget ID (use list_budgets to find available IDs)
    """
    budget = await _shared.cache.get_budget(budget_id)
    return serialize(budget)
