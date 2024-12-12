"""base.py"""

from datetime import datetime, timezone
from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]
DataT = TypeVar("DataT")


class StatusCode(int, Enum):
    """status code"""
    
    SUCCESS = 200
    ERROR = 400
    NOT_FOUND = 404
    TOO_MANY_REQUESTS = 429
    NOT_APPROVED = 403


class BaseMixin(PydanticBaseModel):
    """base mixin"""

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    model_config = ConfigDict(use_enum_values=True)


class ResponseModel(Generic[DataT], PydanticBaseModel):
    """response model"""

    code: StatusCode = Field(..., description="Response status code")
    msg: Optional[str] = Field(default=None, description="Response message")
    data: Optional[DataT] = Field(default=None, description="Response data")

    model_config = ConfigDict(use_enum_values=True)
