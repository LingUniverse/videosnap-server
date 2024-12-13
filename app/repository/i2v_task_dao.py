"""
Create/Remove/Update/Delete database operations
"""
import logging
import random
from typing import Optional
from typing import Any
from uuid import UUID

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.i2v_task_model import I2vTask
from app.schema.i2v_task_schema import I2vType, VideoGenerationProvider

logger = logging.getLogger(__name__)

async def create_i2v_task(
    db: AsyncSession,
    source_image_filename: str,
    video_provider: VideoGenerationProvider,
    i2v_type: I2vType
) -> I2vTask:
    """
    create i2v task
    """
    task = I2vTask(
        source_image_filename=source_image_filename,
        video_generation_provider=video_provider,
        i2v_type=i2v_type
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

async def update_i2v_task(
    db: AsyncSession,
    task_id: UUID,
    update_data: dict[str, Any]
) -> I2vTask | None:
    """
    update i2v task
    """
    result = await db.execute(
        db.query(I2vTask).filter(I2vTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task:
        for key, value in update_data.items():
            setattr(task, key, value)
        await db.commit()
        await db.refresh(task)
    return task

async def get_i2v_task_by_id(
    db: AsyncSession,
    task_id: UUID
) -> I2vTask | None:
    """
    get i2v task
    """
    result = await db.execute(
        db.query(I2vTask).filter(I2vTask.id == task_id)
    )
    return result.scalar_one_or_none()