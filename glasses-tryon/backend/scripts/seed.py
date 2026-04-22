"""Seed the database with sample glasses products."""
import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.models.product import Product

SAMPLES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Classic Aviator",
        "brand": "RayVision",
        "price": 129.99,
        "shape": "aviator",
        "color": "gold",
        "description": "Timeless gold aviator frames with UV-protective lenses.",
        "image_url": "https://placehold.co/600x300/png?text=Aviator+Gold",
        "bridge_x": 0.50, "bridge_y": 0.38,
        "left_temple_x": 0.05, "left_temple_y": 0.35,
        "right_temple_x": 0.95, "right_temple_y": 0.35,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Retro Round",
        "brand": "OakleyLite",
        "price": 89.95,
        "shape": "round",
        "color": "tortoise",
        "description": "Vintage-inspired round frames in a warm tortoiseshell finish.",
        "image_url": "https://placehold.co/600x300/png?text=Round+Tortoise",
        "bridge_x": 0.50, "bridge_y": 0.40,
        "left_temple_x": 0.05, "left_temple_y": 0.38,
        "right_temple_x": 0.95, "right_temple_y": 0.38,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Modern Square",
        "brand": "FrameCo",
        "price": 149.00,
        "shape": "square",
        "color": "black",
        "description": "Bold matte-black square frames for a contemporary look.",
        "image_url": "https://placehold.co/600x300/png?text=Square+Black",
        "bridge_x": 0.50, "bridge_y": 0.36,
        "left_temple_x": 0.04, "left_temple_y": 0.34,
        "right_temple_x": 0.96, "right_temple_y": 0.34,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Cat-Eye Glam",
        "brand": "LuxeOptics",
        "price": 179.50,
        "shape": "cat-eye",
        "color": "rose gold",
        "description": "Elegant rose-gold cat-eye frames with a feminine flair.",
        "image_url": "https://placehold.co/600x300/png?text=CatEye+RoseGold",
        "bridge_x": 0.50, "bridge_y": 0.37,
        "left_temple_x": 0.04, "left_temple_y": 0.32,
        "right_temple_x": 0.96, "right_temple_y": 0.32,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Slim Oval",
        "brand": "VisionPlus",
        "price": 99.00,
        "shape": "oval",
        "color": "silver",
        "description": "Lightweight silver oval frames perfect for everyday wear.",
        "image_url": "https://placehold.co/600x300/png?text=Oval+Silver",
        "bridge_x": 0.50, "bridge_y": 0.39,
        "left_temple_x": 0.06, "left_temple_y": 0.37,
        "right_temple_x": 0.94, "right_temple_y": 0.37,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Wide Rectangle",
        "brand": "BoldLens",
        "price": 119.00,
        "shape": "rectangle",
        "color": "navy blue",
        "description": "Wide navy-blue rectangular frames with a professional edge.",
        "image_url": "https://placehold.co/600x300/png?text=Rectangle+Navy",
        "bridge_x": 0.50, "bridge_y": 0.35,
        "left_temple_x": 0.03, "left_temple_y": 0.33,
        "right_temple_x": 0.97, "right_temple_y": 0.33,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Sporty Aviator",
        "brand": "RayVision",
        "price": 159.99,
        "shape": "aviator",
        "color": "gunmetal",
        "description": "Gunmetal aviator with polarized lenses, built for active lifestyles.",
        "image_url": "https://placehold.co/600x300/png?text=Aviator+Gunmetal",
        "bridge_x": 0.50, "bridge_y": 0.38,
        "left_temple_x": 0.05, "left_temple_y": 0.35,
        "right_temple_x": 0.95, "right_temple_y": 0.35,
    },
]


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=True)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    now = datetime.now(timezone.utc)

    async with Session() as session:
        for data in SAMPLES:
            product = Product(**data, created_at=now, updated_at=now)
            session.add(product)
        await session.commit()
    await engine.dispose()
    print(f"Seeded {len(SAMPLES)} products.")


if __name__ == "__main__":
    asyncio.run(seed())
