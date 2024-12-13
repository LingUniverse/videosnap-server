"""i2v task schema"""

from enum import Enum
from pydantic import BaseModel
from app.schema.base import BaseMixin

class VideoGenerationProvider(str, Enum):
    "video provider"
    
    MINIMAX_VIDEO_01 = "MINIMAX/video-01"

class I2vType(str, Enum):
    """video type"""

    IMAGINATIVE = "imaginative"  # 幻想版
    REALISTIC = "realistic"      # 物理版

class I2vTaskCreateReuqest(BaseModel):
    """i2v Task Create Request"""

    type: I2vType
    image_base64: str

class I2vTaskResponse(BaseModel):
    """I2v Task Response"""

    tid: str
