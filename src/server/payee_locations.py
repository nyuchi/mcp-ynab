from src.server import _shared
from src.server._shared import serialize, serialize_list


@_shared.mcp.tool()
@_shared.handle_errors
async def list_payee_locations(plan_id: str) -> str:
    """List all payee locations in a plan.

    Args:
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    locations = await _shared.cache.get_payee_locations(plan_id)
    return serialize_list(locations)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_payee_location(payee_location_id: str, plan_id: str) -> str:
    """Get a single payee location.

    Args:
        payee_location_id: The payee location ID
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    location = await _shared.cache.get_payee_location(payee_location_id, plan_id)
    return serialize(location)


@_shared.mcp.tool()
@_shared.handle_errors
async def get_payee_locations_by_payee(payee_id: str, plan_id: str) -> str:
    """Get all locations for a specific payee.

    Args:
        payee_id: The payee ID
        plan_id: The plan ID (use list_plans to find available IDs)
    """
    locations = await _shared.cache.get_payee_locations_by_payee(payee_id, plan_id)
    return serialize_list(locations)
