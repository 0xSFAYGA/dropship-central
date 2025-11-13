from fastapi import APIRouter
from app.api.v1.endpoints import auth, products, listings, stores, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


