from src.server import _shared
from src.server._shared import serialize


@_shared.mcp.tool()
@_shared.handle_errors
async def get_user() -> str:
    """Get the authenticated user's information."""
    user = await _shared.cache.get_user()
    return serialize(user)
