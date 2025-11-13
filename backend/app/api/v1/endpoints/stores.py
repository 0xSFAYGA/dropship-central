from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.user import User as DBUser
from app.models.listing import StoreAccount as DBStoreAccount
from app.schemas.listing import StoreAccountCreate, StoreAccountUpdate, StoreAccount as StoreAccountSchema
from app.schemas.common import SuccessResponse
from app.core.exceptions import NotFoundException
from app.api.v1.endpoints.products import get_current_user

router = APIRouter()

@router.get("/", response_model=List[StoreAccountSchema])
async def get_stores(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Retrieve a list of connected store accounts for the current user.
    """
    result = await db.execute(select(DBStoreAccount).where(DBStoreAccount.user_id == current_user.id))
    stores = result.scalars().all()
    return stores

@router.post("/connect", response_model=StoreAccountSchema, status_code=status.HTTP_201_CREATED)
async def connect_store(
    store_in: StoreAccountCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Connect a new store account.
    (This is a simplified version, a real implementation would involve an OAuth2 flow)
    """
    db_store = DBStoreAccount(**store_in.model_dump(), user_id=current_user.id)
    db.add(db_store)
    await db.commit()
    await db.refresh(db_store)
    return db_store

@router.post("/{store_id}/disconnect", response_model=SuccessResponse)
async def disconnect_store(
    store_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[DBUser, Depends(get_current_user)],
):
    """
    Disconnect a store account.
    """
    result = await db.execute(select(DBStoreAccount).where(DBStoreAccount.id == store_id, DBStoreAccount.user_id == current_user.id))
    store = result.scalar_one_or_none()
    if not store:
        raise NotFoundException(detail="Store account not found")

    # In a real scenario, you would revoke tokens and clean up resources.
    # For now, we'll just mark it as disconnected.
    store.is_connected = False
    store.oauth_token = None
    store.oauth_refresh_token = None
    store.api_key = None
    store.api_secret = None

    await db.commit()
    return SuccessResponse(message="Store account disconnected successfully")
