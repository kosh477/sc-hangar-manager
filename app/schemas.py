"""Pydantic schemas for request/response validation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.entities import ALLOWED_SHIP_PART_CLASSES


class ApiSchema(BaseModel):
    """Base schema with ORM compatibility."""

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(ApiSchema):
    name: str = Field(min_length=1, max_length=128)
    email: EmailStr
    login: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=255)


class UserResponse(ApiSchema):
    id: int
    name: str
    email: str
    login: str


class ShipCreateRequest(ApiSchema):
    vendor: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=128)


class ShipResponse(ApiSchema):
    id: int
    vendor: str
    model: str
    name: str


class PartTypeCreateRequest(ApiSchema):
    type: str = Field(min_length=1, max_length=128)
    isReplaceble: bool = False


class PartTypeResponse(ApiSchema):
    id: int
    type: str
    isReplaceble: bool


class PartCreateRequest(ApiSchema):
    vendor: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=128)
    class_: str = Field(alias="class")
    size: int = Field(ge=1, le=10)
    partTypeId: int = Field(gt=0)

    @field_validator("class_")
    @classmethod
    def validate_class(cls, value: str):
        if value not in ALLOWED_SHIP_PART_CLASSES:
            raise ValueError("class must be one of allowed ship part classes")
        return value


class PartResponse(ApiSchema):
    id: int
    vendor: str
    model: str
    class_: str = Field(alias="class")
    size: int
    partTypeId: int
    partType: PartTypeResponse


class UserShipAssignmentRequest(ApiSchema):
    shipId: int = Field(gt=0)
    isDeleted: bool = False


class UserPartAssignmentRequest(ApiSchema):
    partId: int = Field(gt=0)
    isDeleted: bool = False


class ShipPartAssignmentRequest(ApiSchema):
    partId: int = Field(gt=0)


class ApiErrorResponse(ApiSchema):
    error: str
    details: list[str] | None = None

