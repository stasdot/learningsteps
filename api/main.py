from contextlib import asynccontextmanager
import logging
import time
import uuid

from fastapi import FastAPI, Request
from dotenv import load_dotenv

from repositories.postgres_repository import PostgresDB
from routers.journal_router import router as journal_router
from routers.auth_router import router as auth_router

# load env vars from .env
load_dotenv(override=False)

# TODO: move logging config to dedicated logging module
# basic console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# app-level logger
logger = logging.getLogger("app")

# ---------------------------------------------------------
# request id + request logging middleware
# ---------------------------------------------------------
# TODO: extract middleware into separate module if it grows

async def request_context_middleware(request: Request, call_next):
    start_time = time.time()

    # generate or reuse request id
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)

    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        "%s %s %s %sms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        extra={"request_id": request_id},
    )

    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------
# app startup / shutdown lifecycle
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application startup")

    # TODO: replace with explicit DB health check method
    try:
        async with PostgresDB() as db:
            await db.get_all_entries()  # cheap connectivity check
            logger.info("database connection successful")
    except Exception as exc:
        logger.warning("database connection failed on startup: %s", exc)

    yield

    logger.info("application shutdown")


# ---------------------------------------------------------
# fastapi app instance
# ---------------------------------------------------------
app = FastAPI(
    title="LearningSteps API",
    description="A simple learning journal API for tracking daily work, struggles, and intentions",
    lifespan=lifespan
)

# register middleware
app.middleware("http")(request_context_middleware)

# ---------------------------------------------------------
# health check endpoint
# ---------------------------------------------------------
@app.get("/health", tags=["health"])
async def health_check():
    db_status = "unknown"

    try:
        async with PostgresDB() as db:
            await db.get_all_entries()
            db_status = "ok"
    except Exception:
        db_status = "unreachable"

    overall_status = "ok" if db_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "database": db_status,
    }


# ---------------------------------------------------------
# versioned journal routes
# ---------------------------------------------------------
# TODO: introduce additional API versions when breaking changes are needed
app.include_router(
    auth_router,
)

app.include_router(
    journal_router,
    prefix="/v1",
    tags=["journal"]
)

# confirm app start
logger.info("learningsteps api started")
