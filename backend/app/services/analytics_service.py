from datetime import date, timedelta
from decimal import Decimal
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.listing import MarketplaceData
from backend.app.services.schemas import (
    DashboardAnalytics,
    TrendPoint,
    ProfitabilityReport,
    ProductMetric,
)
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    async def compute_dashboard(
        self, user_id: int, db: AsyncSession, period: str = "monthly"
    ) -> DashboardAnalytics:
        """
        Compute dashboard analytics for a user.

        Args:
            user_id: The ID of the user.
            db: The database session.
            period: The time period for the analytics ('daily', 'weekly', 'monthly').

        Returns:
            DashboardAnalytics: The computed dashboard analytics.
        """
        # Simplified implementation. A real implementation would be more complex.
        # Caching logic is also omitted for brevity.

        if period == "daily":
            days = 1
        elif period == "weekly":
            days = 7
        else:
            days = 30

        start_date = date.today() - timedelta(days=days)

        stmt = (
            select(
                func.sum(MarketplaceData.views).label("total_views"),
                func.sum(MarketplaceData.clicks).label("total_clicks"),
                func.sum(MarketplaceData.sales).label("total_sales"),
                func.sum(MarketplaceData.revenue).label("total_revenue"),
                func.sum(MarketplaceData.profit).label("total_profit"),
            )
            .join(MarketplaceData.listing)
            .where(MarketplaceData.listing.user_id == user_id)
            .where(MarketplaceData.date >= start_date)
        )

        result = await db.execute(stmt)
        row = result.first()

        total_views = row.total_views or 0
        total_clicks = row.total_clicks or 0
        total_sales = row.total_sales or 0
        total_revenue = row.total_revenue or Decimal(0)
        total_profit = row.total_profit or Decimal(0)

        click_through_rate = (
            (total_clicks / total_views) * 100 if total_views > 0 else 0.0
        )
        conversion_rate = (
            (total_sales / total_clicks) * 100 if total_clicks > 0 else 0.0
        )

        # Top products logic is simplified
        top_products_by_revenue: List[ProductMetric] = []
        top_products_by_profit: List[ProductMetric] = []

        return DashboardAnalytics(
            total_views=total_views,
            total_clicks=total_clicks,
            total_sales=total_sales,
            total_revenue=total_revenue,
            total_profit=total_profit,
            click_through_rate=click_through_rate,
            conversion_rate=conversion_rate,
            top_products_by_revenue=top_products_by_revenue,
            top_products_by_profit=top_products_by_profit,
        )

    async def get_trends(
        self, user_id: int, db: AsyncSession, days: int = 30, metric: str = "revenue"
    ) -> List[TrendPoint]:
        """
        Get trends for a given metric over a period of days.

        Args:
            user_id: The ID of the user.
            db: The database session.
            days: The number of days to get trends for.
            metric: The metric to get trends for ('revenue' or 'profit').

        Returns:
            A list of TrendPoints.
        """
        start_date = date.today() - timedelta(days=days)
        metric_column = (
            MarketplaceData.revenue if metric == "revenue" else MarketplaceData.profit
        )

        stmt = (
            select(
                MarketplaceData.date,
                func.sum(metric_column).label("value"),
            )
            .join(MarketplaceData.listing)
            .where(MarketplaceData.listing.user_id == user_id)
            .where(MarketplaceData.date >= start_date)
            .group_by(MarketplaceData.date)
            .order_by(MarketplaceData.date.asc())
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [TrendPoint(date=row.date, value=row.value) for row in rows]

    async def compute_profitability(
        self, listing_id: int, db: AsyncSession
    ) -> ProfitabilityReport:
        """
        Compute a profitability report for a listing.

        Args:
            listing_id: The ID of the listing.
            db: The database session.

        Returns:
            A ProfitabilityReport.
        """
        stmt = select(
            func.sum(MarketplaceData.revenue).label("total_revenue"),
            func.sum(MarketplaceData.cost_of_goods_sold).label("total_cost"),
            func.sum(MarketplaceData.profit).label("total_profit"),
            func.min(MarketplaceData.date).label("best_day"),  # Simplified
            func.max(MarketplaceData.date).label("worst_day"),  # Simplified
        ).where(MarketplaceData.listing_id == listing_id)

        result = await db.execute(stmt)
        row = result.first()

        total_revenue = row.total_revenue or Decimal(0)
        total_cost = row.total_cost or Decimal(0)
        total_profit = row.total_profit or Decimal(0)
        margin = (total_profit / total_revenue) if total_revenue > 0 else 0.0

        # Average daily revenue logic is simplified
        average_daily_revenue = Decimal(0)

        return ProfitabilityReport(
            total_revenue=total_revenue,
            total_cost=total_cost,
            total_profit=total_profit,
            margin=float(margin),
            best_day=row.best_day or date.today(),
            worst_day=row.worst_day or date.today(),
            average_daily_revenue=average_daily_revenue,
        )
