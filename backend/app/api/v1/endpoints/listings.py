from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User as DBUser
from app.models.listing import Listing as DBListing
from app.schemas.listing import ListingCreate, ListingUpdate, Listing as ListingSchema
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.core.exceptions import NotFoundException
from app.api.v1.endpoints.products import get_current_user

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[ListingSchema])
async def get_listings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    """
    Retrieve a paginated list of listings for the current user.
    """
    offset = (page - 1) * size
    result = await db.execute(
        select(DBListing)
        .where(DBListing.user_id == current_user.id)
        .options(selectinload(DBListing.marketplace_data))
        .offset(offset)
        .limit(size)
    )
    listings = result.scalars().all()

    count_result = await db.execute(select(func.count(DBListing.id)).where(DBListing.user_id == current_user.id))
    total = count_result.scalar_one()

    return PaginatedResponse(items=listings, total=total, page=page, size=size)

@router.post("/", response_model=ListingSchema, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_in: ListingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Create a new listing.
    """
    db_listing = DBListing(**listing_in.model_dump(), user_id=current_user.id)
    db.add(db_listing)
    await db.commit()
    await db.refresh(db_listing)
    return db_listing

@router.get("/{listing_id}", response_model=ListingSchema)
async def get_listing(
    listing_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Get a single listing by ID.
    """
    result = await db.execute(
        select(DBListing)
        .where(DBListing.id == listing_id, DBListing.user_id == current_user.id)
        .options(selectinload(DBListing.marketplace_data))
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise NotFoundException(detail="Listing not found")
    return listing

@router.put("/{listing_id}", response_model=ListingSchema)
async def update_listing(
    listing_id: int,
    listing_in: ListingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Update a listing.
    """
    result = await db.execute(select(DBListing).where(DBListing.id == listing_id, DBListing.user_id == current_user.id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise NotFoundException(detail="Listing not found")

    update_data = listing_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)

    await db.commit()
    await db.refresh(listing)
    return listing

@router.delete("/{listing_id}", response_model=SuccessResponse)
async def delete_listing(
    listing_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Delete a listing.
    """
    result = await db.execute(select(DBListing).where(DBListing.id == listing_id, DBListing.user_id == current_user.id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise NotFoundException(detail="Listing not found")

    await db.delete(listing)
    await db.commit()
    return SuccessResponse(message="Listing deleted successfully")
