from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import require_admin
from app.schemas.product import ProductCreate, ProductUpdate, ProductRead, ProductListResponse
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    shape: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    q: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    items, total = await product_service.list_products(
        db, shape=shape, color=color,
        min_price=min_price, max_price=max_price,
        q=q, skip=skip, limit=limit,
    )
    return ProductListResponse(items=items, total=total)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
) -> ProductRead:
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _uid: str = Depends(require_admin),
) -> ProductRead:
    return await product_service.create_product(db, data)


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: str,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _uid: str = Depends(require_admin),
) -> ProductRead:
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return await product_service.update_product(db, product, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    _uid: str = Depends(require_admin),
) -> None:
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    await product_service.delete_product(db, product)
