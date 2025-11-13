import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from datetime import datetime

from app.core.redis import get_redis_client
from app.marketplaces.registry import get_marketplace
from app.core.database import get_db
from app.models.listing import Listing as DBListing
from app.models.product import Product as DBProduct
from app.models.admin import Job as DBJob
from app.core.logging import logger

async def syncer_worker():
    """
    Worker that processes listing sync jobs from the Redis queue.
    """
    redis = await get_redis_client()
    db: AsyncSession = await anext(get_db())

    logger.info("syncer_worker_started")
    while True:
        try:
            # Blocking read from the Redis stream
            job_data = await redis.xreadgroup(
                "syncers", "syncer_worker_1", {"syncer:ebay": ">"}, count=1, block=0
            )

            if not job_data:
                continue

            stream, messages = job_data[0]
            message_id, job_params = messages[0]

            job_id = job_params.get("job_id")
            listing_id = job_params.get("listing_id")
            action = job_params.get("action") # e.g., "create", "update_price"
            logger.info("syncer_job_received", job_id=job_id, listing_id=listing_id, action=action)

            # Update job status to RUNNING
            await db.execute(
                update(DBJob).where(DBJob.id == job_id).values(status="RUNNING", started_at=datetime.utcnow())
            )
            await db.commit()

            try:
                result = await db.execute(select(DBListing).where(DBListing.id == listing_id))
                listing = result.scalar_one_or_none()

                if not listing:
                    raise ValueError(f"Listing with id {listing_id} not found")

                marketplace_client = get_marketplace(listing.store_account.marketplace)

                if action == "create":
                    result = await db.execute(select(DBProduct).where(DBProduct.id == listing.product_id))
                    product = result.scalar_one_or_none()
                    if not product:
                        raise ValueError(f"Product with id {listing.product_id} not found")
                    
                    external_id = await marketplace_client.create_listing(product, listing.price)
                    listing.external_listing_id = external_id
                    listing.status = "Active"
                    
                elif action == "update_price":
                    await marketplace_client.update_price(listing.external_listing_id, listing.price)

                await db.commit()

                # Update job status to SUCCESS
                await db.execute(
                    update(DBJob).where(DBJob.id == job_id).values(status="SUCCESS", completed_at=datetime.utcnow())
                )
                await db.commit()

                # Acknowledge the job in Redis
                await redis.xack(stream, "syncers", message_id)
                logger.info("syncer_job_success", job_id=job_id)

            except Exception as e:
                logger.error("syncer_job_failed", job_id=job_id, error=str(e))
                # Update job status to FAILED
                await db.execute(
                    update(DBJob).where(DBJob.id == job_id).values(status="FAILED", error_message=str(e), completed_at=datetime.utcnow())
                )
                await db.commit()

        except Exception as e:
            logger.error("syncer_worker_error", error=str(e))
            await asyncio.sleep(5) # Wait before retrying
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(syncer_worker())
