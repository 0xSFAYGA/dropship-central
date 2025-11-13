from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from decimal import Decimal

class Product(BaseModel):
    """Scraped product data"""
    asin: str  # supplier unique ID
    title: str
    description: Optional[str]
    price: Decimal
    stock: str  # "In Stock" or "5 available"
    rating: Optional[float]
    reviews_count: Optional[int]
    images: List[str]
    url: str

class BaseScraper(ABC):
    """Abstract base for all scrapers"""

    supplier_name: str  # e.g., "amazon", "aliexpress"
    rate_limit: int = 60  # requests per minute
    requires_js: bool = False  # needs browser

    @abstractmethod
    async def get_product(self, product_id: str) -> Product:
        """Fetch single product by ID (ASIN, SKU, etc)

        Args:
            product_id: Supplier-specific product identifier

        Returns:
            Product with all extracted data

        Raises:
            ProductNotFound: If product doesn't exist
            ScrapingError: If scraping fails
        """
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Product]:
        """Search for products matching query

        Args:
            query: Search term (e.g., "wireless headphones")
            limit: Max results to return

        Returns:
            List of products matching search

        Raises:
            ScrapingError: If search fails
        """
        pass

    async def health_check(self) -> bool:
        """Check if scraper is working (can reach supplier)

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to fetch one simple page
            await self.get_product("B000000000")  # Dummy ID
            return True
        except:
            return False
