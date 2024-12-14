"""Routes for resource endpoints"""
import logging
import mimetypes
from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse
from app.utils.file_utils import get_file_path

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/resource/{filename}")
async def get_file_content(filename: str):
    """Return file content for direct browser consumption
    
    Args:
        filename: Name of file to read
        
    Returns:
        FileResponse with appropriate mime type
        
    Raises:
        HTTPException: 404 if file not found or cannot be read
    """
    try:
        file_path = get_file_path(filename)
        content_type, _ = mimetypes.guess_type(filename)
        
        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=filename
        )
        
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
    except Exception as e:
        logger.error(f"Error reading file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cannot read file {filename}")
