"""app dependencies"""
from app.settings import SETTINGS

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from app.settings import SETTINGS
from app.repository.database import AsyncSessionLocal

import logging
logger = logging.getLogger(__name__)

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    """get api key"""

    if not SETTINGS.BOARDGAME_API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API key is not set"
        )
    if api_key_header != SETTINGS.BOARDGAME_API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
    return api_key_header

async def get_db():
    """Get the database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

