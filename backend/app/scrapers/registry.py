from typing import Dict, Optional
from .base import BaseScraper
from .amazon import AmazonScraper
import logging

logger = logging.getLogger(__name__)

class ScraperRegistry:
    """Central registry for all scrapers"""

    _scrapers: Dict[str, BaseScraper] = {}

    @classmethod
    def register(cls, scraper: BaseScraper):
        """Register a scraper"""
        name = scraper.supplier_name
        cls._scrapers[name] = scraper
        logger.info("scraper_registered", supplier=name)

    @classmethod
    def get(cls, supplier_name: str) -> BaseScraper:
        """Get scraper by supplier name"""
        if supplier_name not in cls._scrapers:
            raise ValueError(f"Unknown scraper: {supplier_name}")
        return cls._scrapers[supplier_name]

    @classmethod
    def list_scrapers(cls) -> list:
        """List all registered scrapers"""
        return list(cls._scrapers.keys())

# Auto-register built-in scrapers
ScraperRegistry.register(AmazonScraper())
# Add more: ScraperRegistry.register(AliExpressScraper())

# Export for easy import
def get_scraper(supplier_name: str) -> BaseScraper:
    return ScraperRegistry.get(supplier_name)