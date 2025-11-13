from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.product import Product, PriceHistory
from backend.app.models.listing import Listing
from backend.app.models.admin import Alert
from backend.app.services.schemas import PolicyViolation
import logging

logger = logging.getLogger(__name__)


class PolicyEngine:
    async def check_policies(
        self, product_id: int, db: AsyncSession
    ) -> List[PolicyViolation]:
        """
        Run all policy checks for a given product.

        Args:
            product_id: The ID of the product to check.
            db: The database session.

        Returns:
            A list of policy violations.
        """
        violations = []
        product = await db.get(
            Product,
            product_id,
            options=[selectinload(Product.listings)],
        )
        if not product:
            logger.warning(f"Product with id {product_id} not found for policy check.")
            return []

        low_stock_violation = await self.check_low_stock(product, db)
        if low_stock_violation:
            violations.append(low_stock_violation)

        price_drop_violation = await self.check_price_drop(product, db)
        if price_drop_violation:
            violations.append(price_drop_violation)

        for listing in product.listings:
            margin_violation = await self.check_margin(product, listing, db)
            if margin_violation:
                violations.append(margin_violation)

            duplicate_violation = await self.check_duplicate_listings(
                product, listing.store_account_id, db
            )
            if duplicate_violation:
                violations.append(duplicate_violation)

        for violation in violations:
            alert = Alert(
                user_id=product.user_id,
                type=f"policy_trigger:{violation.policy_name}",
                product_id=product_id,
                severity=violation.severity,
                message=f"Policy violation: {violation.policy_name}",
                data=violation.details,
            )
            db.add(alert)

        await db.commit()
        return violations

    async def check_low_stock(
        self, product: Product, db: AsyncSession, threshold: int = 5
    ) -> Optional[PolicyViolation]:
        """
        Check for low stock and auto-pause listings if necessary.

        Args:
            product: The product to check.
            db: The database session.
            threshold: The low stock threshold.

        Returns:
            A PolicyViolation if stock is low, otherwise None.
        """
        if product.stock is not None and product.stock < threshold:
            for listing in product.listings:
                if listing.status == "Active":
                    listing.status = "Paused"
                    listing.status_reason = "low_stock"
            return PolicyViolation(
                policy_name="low_stock",
                severity="warning",
                details={"stock": product.stock, "threshold": threshold},
            )
        return None

    async def check_margin(
        self,
        product: Product,
        listing: Listing,
        db: AsyncSession,
        min_margin: float = 0.15,
    ) -> Optional[PolicyViolation]:
        """
        Check if the profit margin for a listing is below a minimum.

        Args:
            product: The product.
            listing: The listing.
            db: The database session.
            min_margin: The minimum profit margin.

        Returns:
            A PolicyViolation if the margin is too low, otherwise None.
        """
        # This is a simplified margin calculation.
        # A real implementation would need to account for fees, shipping, etc.
        if product.price > 0:
            margin = (listing.price - product.price) / listing.price
            if margin < min_margin:
                return PolicyViolation(
                    policy_name="low_margin",
                    severity="warning",
                    details={"margin": float(margin), "required": min_margin},
                )
        return None

    async def check_price_drop(
        self, product: Product, db: AsyncSession, drop_threshold_percent: float = 0.05
    ) -> Optional[PolicyViolation]:
        """
        Check for a significant price drop.

        Args:
            product: The product to check.
            db: The database session.
            drop_threshold_percent: The price drop threshold.

        Returns:
            A PolicyViolation if a significant price drop is detected, otherwise None.
        """
        stmt = (
            select(PriceHistory)
            .where(PriceHistory.product_id == product.id)
            .order_by(PriceHistory.recorded_at.desc())
            .limit(2)
        )
        result = await db.execute(stmt)
        price_history = result.scalars().all()

        if len(price_history) == 2:
            old_price = price_history[1].new_price
            new_price = price_history[0].new_price
            if old_price > 0:
                percent_change = (new_price - old_price) / old_price
                if percent_change < -drop_threshold_percent:
                    return PolicyViolation(
                        policy_name="price_drop",
                        severity="info",
                        details={
                            "percent": float(percent_change),
                            "threshold": -drop_threshold_percent,
                        },
                    )
        return None

    async def check_duplicate_listings(
        self, product: Product, store_account_id: int, db: AsyncSession
    ) -> Optional[PolicyViolation]:
        """
        Check for duplicate listings of the same product on the same store.

        Args:
            product: The product to check.
            store_account_id: The ID of the store account.
            db: The database session.

        Returns:
            A PolicyViolation if duplicate listings are found, otherwise None.
        """
        stmt = (
            select(Listing)
            .where(Listing.product_id == product.id)
            .where(Listing.store_account_id == store_account_id)
        )
        result = await db.execute(stmt)
        listings = result.scalars().all()

        if len(listings) > 1:
            return PolicyViolation(
                policy_name="duplicate_listings",
                severity="warning",
                details={"count": len(listings)},
            )
        return None
