from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

# StoreAccount Schemas
class StoreAccountBase(BaseModel):
    marketplace: str
    account_name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    oauth_token: Optional[str] = None
    oauth_refresh_token: Optional[str] = None
    oauth_expires_at: Optional[datetime] = None
    is_connected: Optional[bool] = False
    last_synced_at: Optional[datetime] = None

class StoreAccountCreate(StoreAccountBase):
    user_id: int

class StoreAccountUpdate(StoreAccountBase):
    pass

class StoreAccountInDBBase(StoreAccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class StoreAccount(StoreAccountInDBBase):
    pass

# MarketplaceData Schemas
class MarketplaceDataBase(BaseModel):
    date: date
    views: Optional[int] = 0
    clicks: Optional[int] = 0
    sales: Optional[int] = 0
    revenue: Optional[Decimal] = Decimal(0.0)
    cost_of_goods_sold: Optional[Decimal] = Decimal(0.0)
    profit: Optional[Decimal] = Decimal(0.0)
    avg_rating_received: Optional[Decimal] = None
    customer_feedbacks: Optional[int] = 0
    notes: Optional[str] = None

class MarketplaceDataCreate(MarketplaceDataBase):
    listing_id: int

class MarketplaceDataInDBBase(MarketplaceDataBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int

class MarketplaceData(MarketplaceDataInDBBase):
    pass

# Listing Schemas
class ListingBase(BaseModel):
    product_id: int
    store_account_id: int
    external_listing_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    price: Decimal
    quantity_available: int
    status: Optional[str] = "Pending"
    status_reason: Optional[str] = None
    ended_at: Optional[datetime] = None

class ListingCreate(ListingBase):
    user_id: int

class ListingUpdate(ListingBase):
    pass

class ListingInDBBase(ListingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class Listing(ListingInDBBase):
    marketplace_data: List[MarketplaceData] = []
