import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.redis import get_redis_client
from app.scrapers.registry import get_scraper
from app.core.database import get_db
from app.models.product import Product as DBProduct, PriceHistory, StockHistory
from app.models.admin import Job as DBJob
from app.core.logging import logger

async def scraper_worker():
    """
    Worker that processes scraping jobs from the Redis queue.
    """
    redis = await get_redis_client()
    db: AsyncSession = await anext(get_db())

    logger.info("scraper_worker_started")
    while True:
        try:
            # Blocking read from the Redis stream
            job_data = await redis.xreadgroup(
                "scrapers", "scraper_worker_1", {"scraper:amazon": ">"}, count=1, block=0
            )

            if not job_data:
                continue

            stream, messages = job_data[0]
            message_id, job_params = messages[0]

            job_id = job_params.get("job_id")
            asin = job_params.get("asin")
            logger.info("scraper_job_received", job_id=job_id, asin=asin)

            # Update job status to RUNNING
            await db.execute(
                update(DBJob).where(DBJob.id == job_id).values(status="RUNNING", started_at=datetime.utcnow())
            )
            await db.commit()

            try:
                scraper = get_scraper("amazon") # Assuming amazon for now
                product_data = await scraper.get_product(asin)

                # Save product to DB
                result = await db.execute(select(DBProduct).where(DBProduct.asin == asin))
                db_product = result.scalar_one_or_none()

                if db_product:
                    # Update existing product
                    db_product.title = product_data.title
                    db_product.price = product_data.price
                    db_product.stock = product_data.stock
                    db_product.rating = product_data.rating
                    db_product.reviews_count = product_data.reviews_count
                    db_product.images = product_data.images
                    db_product.url = product_data.url
                    db_product.last_scraped_at = datetime.utcnow()
                else:
                    # Create new product
                    db_product = DBProduct(**product_data.model_dump())
                
                db.add(db_product)
                await db.commit()
                await db.refresh(db_product)

                # Update job status to SUCCESS
                await db.execute(
                    update(DBJob).where(DBJob.id == job_id).values(status="SUCCESS", result={"product_id": db_product.id}, completed_at=datetime.utcnow())
                )
                await db.commit()

                # Acknowledge the job in Redis
                await redis.xack(stream, "scrapers", message_id)
                logger.info("scraper_job_success", job_id=job_id, product_id=db_product.id)

            except Exception as e:
                logger.error("scraper_job_failed", job_id=job_id, error=str(e))
                # Update job status to FAILED
                await db.execute(
                    update(DBJob).where(DBJob.id == job_id).values(status="FAILED", error_message=str(e), completed_at=datetime.utcnow())
                )
                await db.commit()

        except Exception as e:
            logger.error("scraper_worker_error", error=str(e))
            await asyncio.sleep(5) # Wait before retrying
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(scraper_worker())
from datetime import datetime
from sqlalchemy import update
