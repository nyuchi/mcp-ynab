import json
import sys
from functools import wraps

import httpx
from mcp.server.fastmcp import FastMCP

from src.cache.service import CacheService
from src.config import Settings
from src.db.engine import init_db
from src.ynab_client import YNABClient, YNABError

try:
    settings = Settings()  # type: ignore[call-arg]
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("ynab")
client = YNABClient(settings.ynab_api_key, timeout=settings.http_timeout)
cache = CacheService(client, settings)

_db_initialized = False


def dollars_to_milliunits(amount: float) -> int:
    """Convert a dollar amount to YNAB milliunits (1000 = $1.00)."""
    return round(amount * 1000)


def serialize(model, **kwargs) -> str:
    """Serialize a Pydantic model to a JSON string."""
    return json.dumps(model.model_dump(by_alias=True, **kwargs), indent=2)


def serialize_list(models, **kwargs) -> str:
    """Serialize a list of Pydantic models to a JSON string."""
    return json.dumps([m.model_dump(by_alias=True, **kwargs) for m in models], indent=2)


async def _ensure_db():
    global _db_initialized
    if not _db_initialized:
        await init_db(settings.cache_db_path)
        _db_initialized = True


def handle_errors(func):
    """Decorator that catches YNAB and HTTP errors and returns friendly messages."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            await _ensure_db()
            return await func(*args, **kwargs)
        except YNABError as e:
            return json.dumps({"error": e.message, "error_id": e.error_id, "status_code": e.status_code})
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"})
        except httpx.RequestError as e:
            return json.dumps({"error": f"Request failed: {e}"})

    return wrapper
