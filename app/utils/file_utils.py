import os
import base64
import uuid
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Tuple

ASSET_ROOT = "asset"  # Base storage path

async def ensure_directory(directory: str) -> None:
    """Ensure directory exists"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def generate_filename(original_filename: str) -> str:
    """Generate a unique filename with timestamp and random string"""
    ext = os.path.splitext(original_filename)[1]
    return f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}{ext}"

async def generate_file_path(original_filename: str, sub_dir: str = "") -> str:
    """Generate filename for storage"""
    new_filename = generate_filename(original_filename)
    
    if sub_dir:
        new_filename = os.path.join(sub_dir, new_filename)
    
    full_path = os.path.join(ASSET_ROOT, new_filename)
    await ensure_directory(os.path.dirname(full_path))
    
    return new_filename

async def save_base64_file(base64_content: str, original_filename: str, sub_dir: str = "") -> str:
    """Save base64 encoded file content
    
    Args:
        base64_content: Base64 encoded file content
        original_filename: Original filename
        sub_dir: Subdirectory name, e.g. 'images', 'videos'
        
    Returns:
        str: Generated filename
    """
    filename = await generate_file_path(original_filename, sub_dir)
    
    file_content = base64.b64decode(base64_content)
    async with aiofiles.open(os.path.join(ASSET_ROOT, filename), 'wb') as f:
        await f.write(file_content)
        
    return filename

async def save_binary_file(binary_content: bytes, original_filename: str, sub_dir: str = "") -> str:
    """Save binary file content
    
    Args:
        binary_content: Binary file content
        original_filename: Original filename
        sub_dir: Subdirectory name, e.g. 'images', 'videos'
        
    Returns:
        str: Generated filename
    """
    filename = await generate_file_path(original_filename, sub_dir)
    
    async with aiofiles.open(os.path.join(ASSET_ROOT, filename), 'wb') as f:
        await f.write(binary_content)
        
    return filename

def get_file_path(relative_path: str) -> str:
    """Get full physical path of file
    
    Args:
        relative_path: Relative path of file
        
    Returns:
        str: Full physical path of file
    """
    return os.path.join(ASSET_ROOT, relative_path)

async def read_file_to_base64(relative_path: str) -> str:
    """Read file and convert to base64 encoding
    
    Args:
        relative_path: Relative path of file
        
    Returns:
        str: Base64 encoded file content
        
    Raises:
        FileNotFoundError: When file does not exist
        IOError: When failed to read file
    """
    file_path = get_file_path(relative_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        async with aiofiles.open(file_path, "rb") as f:
            file_content = await f.read()
            return base64.b64encode(file_content).decode('utf-8')
    except IOError as e:
        raise IOError(f"Failed to read file: {str(e)}") from e