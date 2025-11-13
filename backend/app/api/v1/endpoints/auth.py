from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.exceptions import ConflictException, UnauthorizedException
from app.config import settings
from app.models.user import User as DBUser, Session as DBSession
from app.schemas.user import UserCreate, User as UserSchema, Session as SessionSchema
from app.schemas.common import SuccessResponse

router = APIRouter()

@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def signup(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user.
    """
    # Check if user with email already exists
    result = await db.execute(select(DBUser).where(DBUser.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise ConflictException(detail="User with this email already exists")

    hashed_password = get_password_hash(user_in.password)
    db_user = DBUser(
        email=user_in.email,
        password_hash=hashed_password,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        tier=user_in.tier,
        api_key=user_in.api_key,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=SessionSchema)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Authenticate user and return access token.
    """
    result = await db.execute(select(DBUser).where(DBUser.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise UnauthorizedException(detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    db_session = DBSession(
        user_id=user.id,
        token=access_token,
        expires_at=datetime.now(timezone.utc) + access_token_expires,
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)

    return db_session

@router.post("/logout", response_model=SuccessResponse)
async def logout():
    """
    Logout user by revoking the current session.
    (Implementation for revoking token will be added later with token management)
    """
    return {"message": "Successfully logged out"}
