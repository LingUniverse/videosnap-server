"""
Module to model mapping database tables
"""
import time
import uuid
from enum import Enum
from typing import Any

from sqlalchemy import BigInteger, Boolean, Column, Date
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Float, Index, Integer, PickleType, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from app.repository.database import BaseMixin
from app.schema.i2v_task_schema import I2vType, TaskStatus

class I2vTask(BaseMixin):
    """Image to Video conversion task"""

    __tablename__ = "i2v_task"
    source_image_filename = Column(String(length=255), nullable=False)
    status: "Column[TaskStatus]" = Column(
        SQLAlchemyEnum(TaskStatus, native_enum=False),
        default=TaskStatus.IDLE,
        nullable=False
    )
    i2v_type: "Column[I2vType]" = Column(
        SQLAlchemyEnum(I2vType, native_enum=False),
        nullable=False
    )
    video_generation_provider = Column(Text, nullable=False)
    video_generation_prompt = Column(Text, nullable=True)
    video_generation_id =  Column(Text, nullable=True)
    output_video_filename = Column(String(length=255), nullable=True)
