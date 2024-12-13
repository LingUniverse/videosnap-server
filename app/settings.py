"""
Module to load configurations from environment
"""
import logging
import os

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

logger = logging.getLogger(__name__)

print(os.getenv("ENV_FILE"))

class AppSettings(BaseSettings):
    """
    Configuration load from environment
    """

    VIDEOSNAP_API_KEY: str

    AZURE_API_KEY: SecretStr
    AZURE_API_BASE: str
    AZURE_API_VERSION: str

    MINIMAX_VIDEO_GENERATION_API_KEY: SecretStr
    MINIMAX_VIDEO_GENERATION_BASE_URL: str
    MINIMAX_VIDEO_GENERATION_CALLBACK_URL: str
    MINIMAX_VIDEO_GENERATION_STATUS_URL: str
    
    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE"), env_file_encoding="utf-8", extra="ignore")


SETTINGS = AppSettings()  # type: ignore
