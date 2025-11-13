from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date


class ProductChangeEvent(BaseModel):
    product_id: int
    has_price_change: bool
    old_price: Optional[Decimal] = None
    new_price: Optional[Decimal] = None
    has_stock_change: bool
    old_stock: Optional[int] = None
    new_stock: Optional[int] = None


class PolicyViolation(BaseModel):
    policy_name: str  # low_stock, low_margin, price_drop, duplicate_listings
    severity: str  # warning, critical
    details: Dict[str, Any]  # context data


class ProductMetric(BaseModel):
    product_id: int
    value: Decimal


class DashboardAnalytics(BaseModel):
    total_views: int
    total_clicks: int
    total_sales: int
    total_revenue: Decimal
    total_profit: Decimal
    click_through_rate: float
    conversion_rate: float
    top_products_by_revenue: List[ProductMetric]
    top_products_by_profit: List[ProductMetric]


class TrendPoint(BaseModel):
    date: date
    value: Decimal


class ProfitabilityReport(BaseModel):
    total_revenue: Decimal
    total_cost: Decimal
    total_profit: Decimal
    margin: float
    best_day: date
    worst_day: date
    average_daily_revenue: Decimal
