import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Depends

from api.dependencies.auth import get_current_user
from api.dependencies.rate_limit import rate_limit
from api.dependencies.cache import get_cache, set_cache, invalidate_cache
from api.repositories.postgres_repository import PostgresDB
from api.services.entry_service import EntryService
from api.models.entry import Entry, EntryCreate, EntryUpdate

logger = logging.getLogger("journal")

router = APIRouter()

# future cross-cutting concerns (intentionally left for later)
# TODO: add authentication middleware -> NOT STARTED (using dependency-based auth stub instead)
# TODO: add request validation middleware (beyond pydantic) -> PARTIALLY DONE (pydantic models)
# TODO: add rate limiting -> DONE (basic dependency-based rate limiting)
# TODO: add api versioning -> DONE (handled in main.py via /v1 prefix)
# TODO: add response caching -> DONE (in-memory cache for read endpoints)


async def get_entry_service() -> AsyncGenerator[EntryService, None]:
    async with PostgresDB() as db:
        yield EntryService(db)


@router.post(
    "/entries",
    dependencies=[Depends(rate_limit)],
)
async def create_entry(
    entry_data: EntryCreate,
    entry_service: EntryService = Depends(get_entry_service),
    user: dict = Depends(get_current_user),  # auth required
):
    """Create a new journal entry."""
    try:

        created_entry = await entry_service.create_entry(entry_data.model_dump())

        # invalidate cached reads
        invalidate_cache("entries:")

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
    """Get all journal entries (public, cached)."""

    cache_key = "entries:all"
    cached = get_cache(cache_key)
    if cached:
        return cached

    entries = await entry_service.get_all_entries()
    response = {
        "entries": entries,
        "count": len(entries),
    }

    set_cache(cache_key, response)
    return response


@router.get("/entries/{entry_id}")
async def get_entry(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Get a single journal entry by ID (public)."""
    entry = await entry_service.get_entry(entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="entry not found")

    return entry


@router.patch(
    "/entries/{entry_id}",
    dependencies=[Depends(rate_limit)],
)
async def update_entry(
    entry_id: str,
    entry_update: EntryUpdate,
    entry_service: EntryService = Depends(get_entry_service),
    user: dict = Depends(get_current_user),  # auth required
):
    """Update an existing journal entry."""
    updated_entry = await entry_service.update_entry(
        entry_id,
        entry_update.model_dump(exclude_unset=True),
    )

    if not updated_entry:
        raise HTTPException(status_code=404, detail="entry not found")

    # invalidate cached reads
    invalidate_cache("entries:")

    return updated_entry


@router.delete(
    "/entries/{entry_id}",
    dependencies=[Depends(rate_limit)],
)
async def delete_entry(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
    user: dict = Depends(get_current_user),  # auth required
):
    """Delete a specific journal entry."""
    entry = await entry_service.get_entry(entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="entry not found")

    await entry_service.delete_entry(entry_id)

    # invalidate cached reads
    invalidate_cache("entries:")

    return {"detail": "entry deleted successfully"}


@router.delete(
    "/entries",
    dependencies=[Depends(rate_limit)],
)
async def delete_all_entries(
    entry_service: EntryService = Depends(get_entry_service),
    user: dict = Depends(get_current_user),  # auth required
):
    """Delete all journal entries."""
    await entry_service.delete_all_entries()

    # invalidate cached reads
    invalidate_cache("entries:")

    return {"detail": "all entries deleted"}
