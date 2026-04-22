from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

GlassesShape = Literal["round", "square", "aviator", "cat-eye", "oval", "rectangle"]


class AnchorPoints(BaseModel):
    bridge_x: float = Field(ge=0.0, le=1.0)
    bridge_y: float = Field(ge=0.0, le=1.0)
    left_temple_x: float = Field(ge=0.0, le=1.0)
    left_temple_y: float = Field(ge=0.0, le=1.0)
    right_temple_x: float = Field(ge=0.0, le=1.0)
    right_temple_y: float = Field(ge=0.0, le=1.0)


class ProductBase(AnchorPoints):
    name: str = Field(min_length=1, max_length=200)
    brand: str = Field(min_length=1, max_length=200)
    price: float = Field(gt=0)
    shape: GlassesShape
    color: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    image_url: str = Field(min_length=1, max_length=500)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductRead]
    total: int
