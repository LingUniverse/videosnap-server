"""
Module for mysql database connection
"""
import logging
import time
import uuid
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import BigInteger, Boolean, Column, Date
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import UUIDType
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DB_USER = os.getenv("DB_USER", "videosnap")
DB_PASS = os.getenv("DB_PASS", "videosnap")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "videosnap")

ASYNC_DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_recycle=3600
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

class TimestampMixin(object):
    """Mixin for timestamp columns"""

    @declared_attr
    def created_at(cls):  # pylint: disable=no-self-argument
        """Timestamp for when the record was created"""
        return Column(BigInteger, default=lambda self: int(time.time() * 1000))

    @declared_attr
    def updated_at(cls):  # pylint: disable=no-self-argument
        """Timestamp for when the record was last updated"""
        return Column(
            BigInteger, default=lambda self: int(time.time() * 1000), onupdate=lambda self: int(time.time() * 1000)
        )


class BaseMixin(TimestampMixin, Base):
    """Base mixin for all models"""

    __abstract__ = True
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)  # type: ignore
