import asyncio
from app.services.tracker_service import track_all_products
from app.core.logging import logger

async def tracker_worker(interval_seconds: int = 3600):
    """
    Worker that periodically tracks all products for changes.
    """
    logger.info("tracker_worker_started", interval_seconds=interval_seconds)
    while True:
        try:
            await track_all_products()
        except Exception as e:
            logger.error("tracker_worker_error", error=str(e))
        
        logger.info("tracker_worker_sleeping", seconds=interval_seconds)
        await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    # Example of how to run the worker
    asyncio.run(tracker_worker(interval_seconds=60))
