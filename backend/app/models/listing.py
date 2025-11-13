from decimal import Decimal
from typing import List, Optional
from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Date, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.base import Base

class StoreAccount(Base):
    """
    Represents a user's connected marketplace account (e.g., eBay, Shopify).
    """
    __tablename__ = "store_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    marketplace: Mapped[str] = mapped_column(String)
    account_name: Mapped[str] = mapped_column(String)
    api_key: Mapped[Optional[str]] = mapped_column(String)
    api_secret: Mapped[Optional[str]] = mapped_column(String)
    oauth_token: Mapped[Optional[str]] = mapped_column(String)
    oauth_refresh_token: Mapped[Optional[str]] = mapped_column(String)
    oauth_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="store_accounts")
    listings: Mapped[List["Listing"]] = relationship(back_populates="store_account", cascade="all, delete-orphan")

class Listing(Base):
    """
    Represents a product listing on a marketplace.
    """
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    store_account_id: Mapped[int] = mapped_column(ForeignKey("store_accounts.id"))
    external_listing_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    quantity_available: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="Pending")
    status_reason: Mapped[Optional[str]] = mapped_column(String)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="listings")
    product: Mapped["Product"] = relationship(back_populates="listings")
    store_account: Mapped["StoreAccount"] = relationship(back_populates="listings")
    marketplace_data: Mapped[List["MarketplaceData"]] = relationship(back_populates="listing", cascade="all, delete-orphan")

class MarketplaceData(Base):
    """
    Stores daily performance data for a marketplace listing.
    """
    __tablename__ = "marketplace_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    date: Mapped[date] = mapped_column(Date)
    views: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    sales: Mapped[int] = mapped_column(Integer, default=0)
    revenue: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=0.0)
    cost_of_goods_sold: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=0.0)
    profit: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=0.0)
    avg_rating_received: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(2, 1))
    customer_feedbacks: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    listing: Mapped["Listing"] = relationship(back_populates="marketplace_data")