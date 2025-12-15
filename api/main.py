from contextlib import asynccontextmanager
from repositories.postgres_repository import PostgresDB
import logging
from fastapi import FastAPI
from dotenv import load_dotenv
from routers.journal_router import router as journal_router

# load env vars from .env
load_dotenv()

# basic console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# app-level logger
logger = logging.getLogger("app")

# app startup / shutdown lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application startup")

    try:
        async with PostgresDB() as db:
            await db.get_all_entries()
            logger.info("database connection successful")
    except Exception as exc:
        logger.warning("database connection failed on startup: %s", exc)

    yield

    logger.info("application shutdown")

# fastapi app instance
app = FastAPI(
    title="LearningSteps API",
    description="A simple learning journal API for tracking daily work, struggles, and intentions",
    lifespan=lifespan  # attach lifecycle hooks
)

# health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    db_status = "unknown"

    try:
        async with PostgresDB() as db:
            await db.get_all_entries()  # cheap connectivity check
            db_status = "ok"
    except Exception:
        db_status = "unreachable"

    overall_status = "ok" if db_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "database": db_status,
    }


# versioned journal routes
app.include_router(
    journal_router,
    prefix="/v1",  # api versioning
    tags=["journal"]
)

# confirm app start
logger.info("learningsteps api started")
