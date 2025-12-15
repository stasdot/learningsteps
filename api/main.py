from contextlib import asynccontextmanager
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
    return {"status": "ok"}

# versioned journal routes
app.include_router(
    journal_router,
    prefix="/v1",  # api versioning
    tags=["journal"]
)

# confirm app start
logger.info("learningsteps api started")
