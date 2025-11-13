class ScrapingError(Exception):
    """Custom exception for scraping errors."""
    pass

class InvalidListingState(Exception):
    """Custom exception for invalid listing state transitions."""
    pass