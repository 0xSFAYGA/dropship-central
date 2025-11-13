from typing import Dict, Type
from app.marketplaces.base import MarketplaceClient
from app.marketplaces.ebay import EBayClient
from app.core.logging import logger

marketplaces: Dict[str, MarketplaceClient] = {
    "ebay": EBayClient(),
    # Add other marketplace clients here as they are created
    # "shopify": ShopifyClient(),
}

def get_marketplace(name: str) -> MarketplaceClient:
    """
    Get a marketplace client instance by name.
    """
    marketplace = marketplaces.get(name)
    if not marketplace:
        logger.error("marketplace_not_found", marketplace_name=name)
        raise ValueError(f"Unknown marketplace: {name}")
    return marketplace
