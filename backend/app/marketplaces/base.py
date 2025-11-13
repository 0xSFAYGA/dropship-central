from abc import ABC, abstractmethod
from app.schemas.product import Product

class MarketplaceClient(ABC):
    """
    Abstract base class for all marketplace clients.
    """

    @abstractmethod
    async def create_listing(self, product: Product, price: float) -> str:
        """
        Create a new listing on the marketplace.
        Returns the external listing ID.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_price(self, listing_id: str, new_price: float) -> bool:
        """
        Update the price of an existing listing.
        Returns True on success, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def withdraw(self, listing_id: str) -> bool:
        """
        Withdraw a listing from the marketplace.
        Returns True on success, False otherwise.
        """
        raise NotImplementedError
