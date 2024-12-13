"""
life time
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
import os
from app.settings import SETTINGS
# from app.service.tts_service import init_voice_ids

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """lifespan"""
    await startup()
    yield
    await shutdown()


async def startup():
    """Actions to run on app startup."""
    logger.info("App is starting up.")
    os.environ["AZURE_API_KEY"] = SETTINGS.AZURE_API_KEY.get_secret_value()
    os.environ["AZURE_API_BASE"] = SETTINGS.AZURE_API_BASE
    os.environ["AZURE_API_VERSION"] = SETTINGS.AZURE_API_VERSION

async def shutdown():
    """Actions to run on app's shutdown."""
    logger.info("App is shutting down.")
