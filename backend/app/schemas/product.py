from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

# Supplier Schemas
class SupplierBase(BaseModel):
    name: str
    base_url: Optional[str] = None
    rate_limit: Optional[int] = None
    requires_js: Optional[bool] = False
    scraper_config: Optional[dict] = None
    is_active: Optional[bool] = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class SupplierInDBBase(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

class Supplier(SupplierInDBBase):
    pass

# PriceHistory Schemas
class PriceHistoryBase(BaseModel):
    old_price: Optional[Decimal] = None
    new_price: Decimal
    price_change_percent: Optional[Decimal] = None
    reason: Optional[str] = None

class PriceHistoryCreate(PriceHistoryBase):
    product_id: int

class PriceHistoryInDBBase(PriceHistoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    recorded_at: datetime

class PriceHistory(PriceHistoryInDBBase):
    pass

# StockHistory Schemas
class StockHistoryBase(BaseModel):
    old_stock: Optional[str] = None
    new_stock: str
    reason: Optional[str] = None

class StockHistoryCreate(StockHistoryBase):
    product_id: int

class StockHistoryInDBBase(StockHistoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    recorded_at: datetime

class StockHistory(StockHistoryInDBBase):
    pass

# Product Schemas
class ProductBase(BaseModel):
    supplier_id: Optional[int] = None
    asin: str
    title: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[str] = None
    rating: Optional[Decimal] = None
    reviews_count: Optional[int] = None
    images: Optional[List[str]] = None
    url: Optional[str] = None
    last_scraped_at: Optional[datetime] = None
    is_archived: Optional[bool] = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductInDBBase(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class Product(ProductInDBBase):
    price_history: List[PriceHistory] = []
    stock_history: List[StockHistory] = []
    # listings: List["Listing"] = [] # Forward reference, will be resolved later

