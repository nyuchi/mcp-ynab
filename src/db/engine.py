from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import event, inspect, text

from src.db.tables import Base

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _set_wal_mode(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


async def init_db(db_path: str) -> None:
    global _engine, _session_factory
    if _engine is not None:
        return

    _engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)

    event.listen(_engine.sync_engine, "connect", _set_wal_mode)

    # Migrate: drop tables with old budget_id column — cache rebuilds automatically
    async with _engine.begin() as conn:
        def _migrate_budget_to_plan(connection):
            insp = inspect(connection)
            for table in ("cached_entities", "server_knowledge"):
                if insp.has_table(table):
                    columns = [c["name"] for c in insp.get_columns(table)]
                    if "budget_id" in columns:
                        connection.execute(text(f"DROP TABLE {table}"))

        await conn.run_sync(_migrate_budget_to_plan)
        await conn.run_sync(Base.metadata.create_all)

    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def get_session() -> AsyncSession:
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _session_factory()


async def close_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
