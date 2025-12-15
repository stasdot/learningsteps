import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Depends

from repositories.postgres_repository import PostgresDB
from services.entry_service import EntryService
from models.entry import Entry, EntryCreate

logger = logging.getLogger("journal")

router = APIRouter()

# future cross-cutting concerns (intentionally left for later)
# TODO: add authentication middleware
# TODO: add request validation middleware (beyond pydantic)
# TODO: add rate limiting
# TODO: add api versioning
# TODO: add response caching


async def get_entry_service() -> AsyncGenerator[EntryService, None]:
    async with PostgresDB() as db:
        yield EntryService(db)


@router.post("/entries")
async def create_entry(
    entry_data: EntryCreate,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Create a new journal entry."""
    try:
        entry = Entry(
            work=entry_data.work,
            struggle=entry_data.struggle,
            intention=entry_data.intention,
        )

        created_entry = await entry_service.create_entry(entry.model_dump())

        return {
            "detail": "entry created successfully",
            "entry": created_entry,
        }

    except Exception as exc:
        logger.exception("failed to create entry")
        raise HTTPException(
            status_code=400,
            detail=f"error creating entry: {str(exc)}",
        )


@router.get("/entries")
async def get_all_entries(
    entry_service: EntryService = Depends(get_entry_service),
):
    """Get all journal entries."""
    entries = await entry_service.get_all_entries()
    return {
        "entries": entries,
        "count": len(entries),
    }


@router.get("/entries/{entry_id}")
async def get_entry(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Get a single journal entry by ID."""
    entry = await entry_service.get_entry(entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="entry not found")

    return entry


@router.patch("/entries/{entry_id}")
async def update_entry(
    entry_id: str,
    entry_update: dict,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Update an existing journal entry."""
    updated_entry = await entry_service.update_entry(entry_id, entry_update)

    if not updated_entry:
        raise HTTPException(status_code=404, detail="entry not found")

    return updated_entry


@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Delete a specific journal entry."""
    entry = await entry_service.get_entry(entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="entry not found")

    await entry_service.delete_entry(entry_id)
    return {"detail": "entry deleted successfully"}


@router.delete("/entries")
async def delete_all_entries(
    entry_service: EntryService = Depends(get_entry_service),
):
    """Delete all journal entries."""
    await entry_service.delete_all_entries()
    return {"detail": "all entries deleted"}
