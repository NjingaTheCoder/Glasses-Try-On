import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, Text, Enum as SAEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


SHAPE_ENUM = SAEnum(
    "round", "square", "aviator", "cat-eye", "oval", "rectangle",
    name="glasses_shape",
)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    shape: Mapped[str] = mapped_column(SHAPE_ENUM, nullable=False)
    color: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)

    bridge_x: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    bridge_y: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    left_temple_x: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    left_temple_y: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    right_temple_x: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    right_temple_y: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
