import logging
import aiohttp
from fastapi import HTTPException

from typing import Optional
from uuid import uuid4
from aiohttp import ClientSession
from app.settings import SETTINGS
from app.dependencies import get_s3_client

logger = logging.getLogger(__name__)

async def upload_to_s3(file_data: bytes, file_type: str) -> Optional[str]:
    """
    General method to upload file data to S3
    :param file_data: The file data to upload
    :param file_type: Type of the file (image, audio, music)
    :return: S3 file path or None
    """
    try:
        file_ext = ".jpg" if file_type == "image" else ".mp3"
        file_path = f"resource/{file_type}/{uuid4().hex}{file_ext}"
        
        async with get_s3_client() as s3_client:
            await s3_client.put_object(
                Bucket=SETTINGS.AWS_S3_BUCKET_NAME,
                Key=file_path,
                Body=file_data
            )
            return f"/{file_path}"
    except Exception as e:
        logger.error("Failed to upload %s to S3: %s", file_type, e)
        return None

async def download_image(image_url: str) -> Optional[bytes]:
    """
    Download an image from a URL
    :param image_url: The URL of the image to download
    :return: Image data in bytes or None
    """
    try:
        async with ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error("Failed to download image from URL: %s", image_url)
                    return None
    except Exception as e:
        logger.error("Failed to download image: %s", e)
        return None

async def upload_image(token: str, file_name: str) -> dict:
    """Upload image to Musisoul by retrieving the file from S3"""
    logger.info("upload_image invoke")
    url = f"{SETTINGS.MUSISOUL_BASE_URL}/upload_img"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 从S3中获取文件内容
    try:
        async with get_s3_client() as s3_client:
            response = await s3_client.get_object(
                Bucket=SETTINGS.AWS_S3_BUCKET_NAME,
                Key=file_name
            )
            file_data = await response['Body'].read()
        
        logger.info("Successfully retrieved file %s from S3", file_name)
        
        # 上传到 Musisoul 服务
        async with aiohttp.ClientSession() as session:
            files = {'init_img': file_data}
            async with session.post(url, headers=headers, data=files) as response:
                if response.status == 200:
                    response_json = await response.json()
                    return response_json['info']
                else:
                    logger.error("HTTP error: %s", await response.text())
                    raise HTTPException(status_code=response.status, detail="Failed to upload image.")
    except Exception as e:
        logger.error("upload image error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error when uploading image.") from e