from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.models import Base  # 导入你的 SQLAlchemy 模型

# this is the Alembic Config object
config = context.config

# ...

target_metadata = Base.metadata  # 设置模型的 metadata

# ... 