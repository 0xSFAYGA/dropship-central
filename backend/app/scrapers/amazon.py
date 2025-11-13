from curl_cffi.requests import AsyncSession, Headers
from bs4 import BeautifulSoup
import random
from typing import Optional, List
from .base import BaseScraper, Product
from ..core.exceptions import ProductNotFound, ScrapingError
# from ..utils.proxy_manager import get_healthy_proxy # This will be created later
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class AmazonScraper(BaseScraper):
    supplier_name = "amazon"
    requires_js = False  # curl-cffi can handle most Amazon pages

    def __init__(self):
        self.base_url = "https://www.amazon.com"
        self.impersonate_browser = "chrome120"

    async def get_product(self, asin: str) -> Product:
        """Fetch Amazon product by ASIN"""
        try:
            url = f"{self.base_url}/dp/{asin}"
            # proxy = await get_healthy_proxy()  # From proxy_pool

            headers = self._get_random_headers()

            async with AsyncSession() as session:
                response = await session.get(
                    url,
                    impersonate=self.impersonate_browser,
                    # proxy=proxy,
                    headers=headers,
                    timeout=10
                )

            if response.status_code == 404:
                raise ProductNotFound(f"ASIN {asin} not found on Amazon")

            if response.status_code != 200:
                raise ScrapingError(f"Failed to fetch {asin}: {response.status_code}")

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            product = self._parse_product(soup, asin, url)

            logger.info("amazon_product_scraped", asin=asin, title=product.title)
            return product

        except Exception as e:
            logger.error("amazon_scrape_failed", asin=asin, error=str(e))
            raise ScrapingError(f"Failed to scrape {asin}: {str(e)}")

    async def search(self, query: str, limit: int = 10) -> List[Product]:
        """Search Amazon products"""
        try:
            url = f"{self.base_url}/s"
            params = {"k": query}
            # proxy = await get_healthy_proxy()
            headers = self._get_random_headers()

            async with AsyncSession() as session:
                response = await session.get(
                    url,
                    params=params,
                    impersonate=self.impersonate_browser,
                    # proxy=proxy,
                    headers=headers
                )

            soup = BeautifulSoup(response.text, "html.parser")
            products = self._parse_search_results(soup)[:limit]

            logger.info("amazon_search_completed", query=query, count=len(products))
            return products

        except Exception as e:
            logger.error("amazon_search_failed", query=query, error=str(e))
            raise ScrapingError(f"Search failed: {str(e)}")

    def _parse_product(self, soup: BeautifulSoup, asin: str, url: str) -> Product:
        """Extract product data from HTML"""
        # Use CSS selectors (adapt from your amazon_poller.py)
        title = soup.select_one("h1 span")
        title = title.text.strip() if title else "Unknown"
        price_text = soup.select_one(".a-price-whole")
        price_text = price_text.text if price_text else "0"
        price = Decimal(price_text.replace("$", "").replace(",", ""))
        stock = self._extract_stock(soup)
        rating = self._extract_rating(soup)
        reviews = self._extract_reviews(soup)
        images = self._extract_images(soup)

        return Product(
            asin=asin,
            title=title,
            price=price,
            stock=stock,
            rating=rating,
            reviews_count=reviews,
            images=images,
            url=url
        )

    def _parse_search_results(self, soup: BeautifulSoup) -> List[Product]:
        """Extract products from search page"""
        products = []
        for item in soup.select("[data-component-type='s-search-result']"):
            asin = item.get("data-asin")
            if not asin:
                continue
            # Parse each search result
            # ... implementation details ...
        return products

    def _get_random_headers(self) -> Headers:
        """Random user agent and headers"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        return Headers({
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def _extract_stock(self, soup) -> str:
        # Implementation from your amazon_poller.py patterns
        return "In Stock"

    def _extract_rating(self, soup) -> Optional[float]:
        # Implementation
        return 4.5

    def _extract_reviews(self, soup) -> Optional[int]:
        # Implementation
        return 100

    def _extract_images(self, soup) -> List[str]:
        # Implementation
        return []
