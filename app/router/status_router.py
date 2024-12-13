"""Routes for the users endpoints"""
import json
import logging
import typing

from dotenv import dotenv_values
from fastapi import APIRouter
from starlette.responses import Response

# from app.settings import SETTINGS

router = APIRouter()
logger = logging.getLogger(__name__)


class PrettyJSONResponse(Response):
    """JSON response with indented formatting"""

    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")

@router.get("/")
async def heartbeat():
    """Heartbeat"""
    return {"status": "ok"}

@router.get("/admin/manifest", response_class=PrettyJSONResponse)
async def manifest():
    """System Settings For Debug"""
    return dotenv_values("./manifest.metadata")
