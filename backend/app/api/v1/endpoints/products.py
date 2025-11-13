from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User as DBUser
from app.models.product import Product as DBProduct
from app.schemas.product import ProductCreate, ProductUpdate, Product as ProductSchema
from app.schemas.common import PaginatedResponse, SuccessResponse, IDSchema
from app.core.exceptions import NotFoundException

router = APIRouter()

# Dependency to get current user from token
async def get_current_user(token: str = Depends(decode_access_token), db: AsyncSession = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    email = token.get("sub")
    result = await db.execute(select(DBUser).where(DBUser.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.get("/", response_model=PaginatedResponse[ProductSchema])
async def get_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    """
    Retrieve a paginated list of products for the current user.
    """
    offset = (page - 1) * size
    result = await db.execute(
        select(DBProduct)
        .where(DBProduct.listings.any(user_id=current_user.id))
        .options(selectinload(DBProduct.price_history), selectinload(DBProduct.stock_history))
        .offset(offset)
        .limit(size)
    )
    products = result.scalars().all()

    count_result = await db.execute(select(func.count(DBProduct.id)).where(DBProduct.listings.any(user_id=current_user.id)))
    total = count_result.scalar_one()

    return PaginatedResponse(items=products, total=total, page=page, size=size)

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Create a new product.
    """
    db_product = DBProduct(**product_in.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Get a single product by ID.
    """
    result = await db.execute(
        select(DBProduct)
        .where(DBProduct.id == product_id, DBProduct.listings.any(user_id=current_user.id))
        .options(selectinload(DBProduct.price_history), selectinload(DBProduct.stock_history))
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundException(detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Update a product.
    """
    result = await db.execute(select(DBProduct).where(DBProduct.id == product_id, DBProduct.listings.any(user_id=current_user.id)))
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundException(detail="Product not found")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/{product_id}", response_model=SuccessResponse)
async def delete_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Delete a product.
    """
    result = await db.execute(select(DBProduct).where(DBProduct.id == product_id, DBProduct.listings.any(user_id=current_user.id)))
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundException(detail="Product not found")

    await db.delete(product)
    await db.commit()
    return SuccessResponse(message="Product deleted successfully")

@router.post("/import", response_model=IDSchema, status_code=status.HTTP_202_ACCEPTED)
async def import_product(
    asin: str = Query(..., description="ASIN of the product to import"),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
    current_user: Annotated[DBUser, Depends(get_current_user)] = Depends(get_current_user),
):
    """
    Queue a job to import a product from a supplier.
    """
    # This will be implemented with the jobs system later.
    # For now, we'll just return a dummy job ID.
    return IDSchema(id=123)
