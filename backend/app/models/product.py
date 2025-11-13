from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.base import Base

class Product(Base):
    """
    Represents a product scraped from a supplier.
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"))
    asin: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    stock: Mapped[Optional[str]] = mapped_column(String)
    rating: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(2, 1))
    reviews_count: Mapped[Optional[int]] = mapped_column(Integer)
    images: Mapped[Optional[List[str]]] = mapped_column(JSON)
    url: Mapped[Optional[str]] = mapped_column(String)
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


    price_history: Mapped[List["PriceHistory"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    stock_history: Mapped[List["StockHistory"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    listings: Mapped[List["Listing"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    supplier: Mapped["Supplier"] = relationship(back_populates="products")


class PriceHistory(Base):
    """
    Records the price changes for a product.
    """
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    old_price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    new_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    price_change_percent: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reason: Mapped[Optional[str]] = mapped_column(String)

    product: Mapped["Product"] = relationship(back_populates="price_history")

class StockHistory(Base):
    """
    Records the stock changes for a product.
    """
    __tablename__ = "stock_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    old_stock: Mapped[Optional[str]] = mapped_column(String)
    new_stock: Mapped[str] = mapped_column(String)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reason: Mapped[Optional[str]] = mapped_column(String)

    product: Mapped["Product"] = relationship(back_populates="stock_history")

class Supplier(Base):
    """
    Represents a supplier from which products are scraped.
    """
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    base_url: Mapped[Optional[str]] = mapped_column(String)
    rate_limit: Mapped[Optional[int]] = mapped_column(Integer)
    requires_js: Mapped[bool] = mapped_column(Boolean, default=False)
    scraper_config: Mapped[Optional[dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


    products: Mapped[List["Product"]] = relationship(back_populates="supplier")