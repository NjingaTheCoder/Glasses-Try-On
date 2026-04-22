from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def list_products(
    db: AsyncSession,
    shape: Optional[str],
    color: Optional[str],
    min_price: Optional[float],
    max_price: Optional[float],
    q: Optional[str],
    skip: int,
    limit: int,
) -> tuple[list[Product], int]:
    stmt = select(Product)
    count_stmt = select(func.count()).select_from(Product)

    if shape:
        stmt = stmt.where(Product.shape == shape)
        count_stmt = count_stmt.where(Product.shape == shape)
    if color:
        stmt = stmt.where(Product.color.ilike(f"%{color}%"))
        count_stmt = count_stmt.where(Product.color.ilike(f"%{color}%"))
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
        count_stmt = count_stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)
        count_stmt = count_stmt.where(Product.price <= max_price)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(Product.name.ilike(pattern) | Product.brand.ilike(pattern))
        count_stmt = count_stmt.where(
            Product.name.ilike(pattern) | Product.brand.ilike(pattern)
        )

    stmt = stmt.order_by(Product.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    total_result = await db.execute(count_stmt)

    items = list(result.scalars().all())
    total = total_result.scalar_one()
    return items, total


async def get_product(db: AsyncSession, product_id: str) -> Optional[Product]:
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def update_product(
    db: AsyncSession, product: Product, data: ProductUpdate
) -> Product:
    for field, value in data.model_dump().items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product: Product) -> None:
    await db.delete(product)
    await db.commit()
