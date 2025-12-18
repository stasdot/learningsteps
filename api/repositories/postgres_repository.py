import json
import os
import uuid
import asyncpg
from datetime import datetime
from typing import Any, Dict, List, Optional

from repositories.interface_repository import DatabaseInterface


class PostgresDB(DatabaseInterface):
    @staticmethod
    def _now_utc() -> datetime:
        return datetime.utcnow()

    @staticmethod
    def datetime_serialize(obj: Any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"type {type(obj)} not serializable")

    @staticmethod
    def _row_to_entry(row: asyncpg.Record) -> Dict[str, Any]:
        data = json.loads(row["data"]) if row["data"] else {}
        return {
            "id": row["id"],
            "work": data.get("work", ""),
            "struggle": data.get("struggle", ""),
            "intention": data.get("intention", ""),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    async def __aenter__(self):
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is missing")

        self.pool = await asyncpg.create_pool(database_url)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.pool.close()

    async def create_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            entry_id = entry_data.get("id") or str(uuid.uuid4())
            created_at = entry_data.get("created_at") or self._now_utc()
            updated_at = entry_data.get("updated_at") or created_at

            entry_data = {**entry_data, "id": entry_id, "created_at": created_at, "updated_at": updated_at}
            data_json = json.dumps(entry_data, default=self.datetime_serialize)

            query = """
            INSERT INTO entries (id, data, created_at, updated_at)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """
            row = await conn.fetchrow(query, entry_id, data_json, created_at, updated_at)
            return self._row_to_entry(row) if row else {}

    async def get_all_entries(self) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM entries")
            return [self._row_to_entry(r) for r in rows]

    async def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM entries WHERE id = $1", entry_id)
            return self._row_to_entry(row) if row else None

    async def update_entry(self, entry_id: str, updated_data: Dict[str, Any]) -> None:
        updated_at = self._now_utc()
        updated_data = {**updated_data, "id": entry_id, "updated_at": updated_at}
        data_json = json.dumps(updated_data, default=self.datetime_serialize)

        async with self.pool.acquire() as conn:
            query = """
            UPDATE entries
            SET data = $2, updated_at = $3
            WHERE id = $1
            """
            await conn.execute(query, entry_id, data_json, updated_at)

    async def delete_entry(self, entry_id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM entries WHERE id = $1", entry_id)

    async def delete_all_entries(self) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM entries")
