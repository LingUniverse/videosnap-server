"""i2v task schema"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from app.schema.base import BaseMixin

class VideoGenerationProvider(str, Enum):
    "video provider"
    
    MINIMAX_VIDEO_01 = "MINIMAX/video-01"

class TaskStatus(Enum):
    """Task Status"""
    IDLE = "idle"
    PROMPT_GENERATED = "prompt_generated"
    TASK_SUBMITTED = "task_submitted"
    TASK_COMPLETED = "task_completed"
    FAILED = "failed"

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

    id: str
    source_image_filename: str
    status: TaskStatus
    i2v_type: I2vType
    video_generation_id: Optional[str]
    output_video_filename: Optional[str]
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if hasattr(v, 'hex'):
            return str(v)
        return v