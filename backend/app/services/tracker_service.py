import asyncio
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.product import Product, PriceHistory, StockHistory
from backend.app.scrapers.registry import get_scraper
from backend.app.services.schemas import ProductChangeEvent
from backend.app.core.exceptions import ScrapingError
import logging

logger = logging.getLogger(__name__)


class TrackerService:
    async def track_product(
        self, product_id: int, db: AsyncSession
    ) -> Optional[ProductChangeEvent]:
        """
        Track price and stock changes for a single product.

        Args:
            product_id: The ID of the product to track.
            db: The database session.

        Returns:
            A ProductChangeEvent if changes are detected, otherwise None.

        Raises:
            ScrapingError: If the scraper fails to fetch the product data.
        """
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.price_history), selectinload(Product.stock_history)
            )
        )
        result = await db.execute(stmt)
        product = result.scalars().first()

        if not product:
            logger.warning(f"Product with id {product_id} not found for tracking.")
            return None

        try:
            scraper = get_scraper(product.supplier.name)
            scraped_product = await scraper.get_product(product.asin)
        except Exception as e:
            logger.error(
                f"Scraping failed for product {product_id}: {e}", exc_info=True
            )
            raise ScrapingError(f"Failed to scrape product {product_id}") from e

        old_price = product.price
        new_price = scraped_product.price
        price_changed = old_price != new_price

        old_stock = product.stock
        new_stock = scraped_product.stock
        stock_changed = old_stock != new_stock

        if not price_changed and not stock_changed:
            return None

        change_event = ProductChangeEvent(
            product_id=product_id,
            has_price_change=price_changed,
            old_price=old_price,
            new_price=new_price,
            has_stock_change=stock_changed,
            old_stock=old_stock,
            new_stock=new_stock,
        )

        if price_changed:
            price_history_entry = PriceHistory(
                product_id=product_id,
                old_price=old_price,
                new_price=new_price,
                price_change_percent=self.get_price_change_percent(
                    old_price, new_price
                ),
            )
            db.add(price_history_entry)
            product.price = new_price

        if stock_changed:
            stock_history_entry = StockHistory(
                product_id=product_id, old_stock=old_stock, new_stock=new_stock
            )
            db.add(stock_history_entry)
            product.stock = new_stock

        await db.commit()
        return change_event

    async def track_multiple_products(
        self, product_ids: List[int], db: AsyncSession
    ) -> List[ProductChangeEvent]:
        """
        Track price and stock changes for multiple products in parallel.

        Args:
            product_ids: A list of product IDs to track.
            db: The database session.

        Returns:
            A list of ProductChangeEvents for products with changes.
        """
        tasks = [self.track_product(product_id, db) for product_id in product_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        change_events = []
        for result in results:
            if isinstance(result, ProductChangeEvent):
                change_events.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error tracking product: {result}", exc_info=result)

        return change_events

    def get_price_change_percent(
        self, old_price: Decimal, new_price: Decimal
    ) -> Decimal:
        """
        Calculate the percentage change between two prices.

        Args:
            old_price: The original price.
            new_price: The new price.

        Returns:
            The percentage change.
        """
        if old_price == 0:
            return Decimal("inf") if new_price > 0 else Decimal(0)
        return ((new_price - old_price) / old_price) * 100
