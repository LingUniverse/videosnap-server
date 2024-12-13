from abc import ABC, abstractmethod
import aiohttp
import json
import logging

from app.schema.i2v_task_schema import VideoGenerationProvider
from app.repository.i2v_task_model import TaskStatus
from app.settings import SETTINGS

logger = logging.getLogger(__name__)

class VideoGenerator(ABC):
    """video generator"""

    @abstractmethod
    async def generate(self, image_base64: str, prompt: str):
        """generate video"""

    @abstractmethod
    async def check_status(self, video_generation_id: str) -> tuple[TaskStatus, str | None]:
        """check status"""

class VideoGeneratorFactory:
    """video generator factory"""

    @staticmethod
    def create(provider: VideoGenerationProvider) -> VideoGenerator:
        """create"""
        if provider.value.startswith("MINIMAX"):
            return MinimaxVideoGenerator()
        else:
            raise ValueError(f"unspport video provider: {provider}")

class MinimaxVideoGenerator(VideoGenerator):
    """minimax video generator"""

    async def generate(self, image_base64, prompt):
        """generate"""
        payload = json.dumps({
            "model": "video-01", 
            "prompt": prompt,
            "first_frame_image": f"data:image/jpeg;base64,{image_base64}",
            "prompt_optimizer": True,
            # "callback_url": SETTINGS.MINIMAX_VIDEO_GENERATION_CALLBACK_URL
        })
        headers = {
            'authorization': f'Bearer {SETTINGS.MINIMAX_VIDEO_GENERATION_API_KEY.get_secret_value()}',
            'Content-Type': 'application/json'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(SETTINGS.MINIMAX_VIDEO_GENERATION_BASE_URL, headers=headers, data=payload) as response:
                    result = await response.text()
                    if response.status != 200:
                        logger.error("Minimax API error - status %d: %s", response.status, result)
                        raise Exception(f"Minimax API error: {response.status} - {result}")
                    
                    logger.info("Minimax video generation response - status %d: %s", response.status, result)
                    response_data = json.loads(result)
                    if response_data.get("base_resp", {}).get("status_code") == 0:
                        return response_data.get("task_id")
                    else:
                        return None
    
        except Exception as e:
            logger.error("Unexpected error when generating video: %s", str(e))
            raise

    async def check_status(self, video_generation_id: str) -> tuple[TaskStatus, str | None]:
        """Check video generation status"""
        try:
            task_status = await self._get_task_status(video_generation_id)
            if task_status.get("status") == "Success":
                download_url = await self._get_download_url(task_status.get("file_id"))
                return TaskStatus.TASK_COMPLETED, download_url
            elif task_status.get("status") == "Failed":
                return TaskStatus.FAILED, None
            else:
                return TaskStatus.TASK_SUBMITTED, None
        except Exception as e:
            logger.error("Error checking video status: %s", str(e))
            return TaskStatus.FAILED, None

    async def _get_task_status(self, video_generation_id: str) -> dict:
        """Get task status"""
        status_url = f"{SETTINGS.MINIMAX_VIDEO_GENERATION_BASE_URL}/query/video_generation"
        headers = {
            'authorization': f'Bearer {SETTINGS.MINIMAX_VIDEO_GENERATION_API_KEY.get_secret_value()}',
            'content-type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{status_url}?task_id={video_generation_id}", headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"API error querying status - status {response.status}")
                result = await response.json()
                if result.get("base_resp", {}).get("status_code") != 0:
                    raise Exception(f"Error in status response: {result}")
                return result

    async def _get_download_url(self, file_id: str) -> str:
        """Get file download URL"""
        file_url = f"{SETTINGS.MINIMAX_VIDEO_GENERATION_BASE_URL}/files/retrieve"
        headers = {
            'authorization': f'Bearer {SETTINGS.MINIMAX_VIDEO_GENERATION_API_KEY.get_secret_value()}',
            'content-type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{file_url}?file_id={file_id}", headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get download URL - status {response.status}")
                result = await response.json()
                download_url = result.get("file", {}).get("download_url")
                if not download_url:
                    raise Exception("Download URL not found")
                return download_url
