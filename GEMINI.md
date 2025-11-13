# Dropship Central - Complete Project Context & Architecture Bible

**Read this file completely before generating ANY code. This is your project's DNA.**

---

## 📍 PROJECT IDENTITY

**Name:** Dropship Central
**Type:** Multi-Marketplace Dropshipping Automation SaaS
**Status:** MVP Development (Started: Nov 12, 2025)
**Target:** Production-ready backend in 10 days
**Tech Era:** 2025 Best Practices

---

## 🎯 PROJECT GOALS

### Primary Goal
Build a **production-grade, extensible backend** for dropshipping automation that:
1. ✅ Scrapes multiple suppliers (Amazon, AliExpress, etc)
2. ✅ Tracks price & stock in real-time
3. ✅ Uploads listings to multiple marketplaces (eBay, Shopify, etc)
4. ✅ Applies business policies automatically (low-stock alerts, margin checks)
5. ✅ Calculates analytics (revenue, profit, trends)
6. ✅ Scales horizontally with async workers

### Secondary Goals
- ✅ Clean, maintainable code
- ✅ Comprehensive testing (80%+ coverage)
- ✅ Easy to extend (plugin systems)
- ✅ Production deployment ready
- ✅ Type-safe (full type hints)
- ✅ Observable (structured logging, metrics)

---

## 🏗️ COMPLETE SYSTEM ARCHITECTURE

### System Components (Big Picture)

```
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  (main.py) - HTTP Requests, Routes, Error Handling          │
└──────────────┬─────────────────────────────┬────────────────┘
               │                             │
        Dependency Injection            Middleware
               │                             │
        ┌──────┴──────┐                    │
        │             │                    │
        ▼             ▼                    ▼
    ┌────────┐   ┌────────┐         ┌──────────┐
    │Database│   │ Redis  │         │ Logging  │
    │  (DB)  │   │(Queue) │         │ Metrics  │
    └────────┘   └────────┘         └──────────┘
        │             │
        │    Job Queue (Redis Streams)
        │    ├─ scraper:amazon
        │    ├─ tracker:all
        │    └─ syncer:ebay
        │
        ▼
    ┌──────────────────────────────┐
    │  Worker Processes            │
    │  (Background, Async)         │
    │                              │
    │  ├─ scraper_worker          │
    │  ├─ tracker_worker          │
    │  └─ syncer_worker           │
    └────┬─────────────┬──────────┘
         │             │
         ▼             ▼
    ┌─────────┐   ┌──────────┐
    │Scrapers │   │Marketplaces
    │(Plugin) │   │(Plugin)
    │         │   │
    │Amazon   │   │eBay
    │Alixprs  │   │Shopify
    │More...  │   │More...
    └─────────┘   └──────────┘
```

### Data Flow: Complete Example

```
USER ACTION: "Scrape Amazon product ASIN B123456"

┌─ STEP 1: API Request ─────────────────────────────────────┐
│ POST /products/import?asin=B123456                         │
│ Header: Authorization: Bearer {jwt_token}                 │
└────────────────────────┬────────────────────────────────┘
                         │ 1. Route handler validates
                         │ 2. Auth check (get_current_user)
                         │ 3. ASIN format validation
                         │
┌────────────────────────▼─────────────────────────────────┐
│ STEP 2: Database Transaction                              │
│ - BEGIN TRANSACTION                                        │
│ - INSERT jobs (status=PENDING, params={asin})            │
│ - Get job_id = 789                                        │
│ - COMMIT                                                  │
└────────────────────────┬──────────────────────────────────┘
                         │ INSTANT RESPONSE to user!
                         │ {"job_id": "789", "status": "queued"}
                         │
┌────────────────────────▼──────────────────────────────────┐
│ STEP 3: Queue Job (Redis Streams)                        │
│ await redis.xadd(                                         │
│   "scraper:amazon",                                       │
│   {                                                       │
│     "job_id": "789",                                      │
│     "asin": "B123456",                                    │
│     "priority": 1,                                        │
│     "retry_count": 0                                      │
│   }                                                       │
│ )                                                         │
└────────────────────────┬──────────────────────────────────┘
                         │
          ┌──────────────┴────────────────────┐
          │                                   │
          ▼ (IN BACKGROUND, SEPARATE PROCESS)▼
┌─ STEP 4: Worker Polling ──┐    ┌─ STEP 5: Worker Polling ──┐
│ scraper_worker #1 polls    │    │ scraper_worker #2 polls    │
│ xreadgroup("scrapers",     │    │ xreadgroup("scrapers",     │
│   "group-1",               │    │   "group-2",               │
│   "scraper:amazon")        │    │   "scraper:amazon")        │
│                            │    │                            │
│ Detects job! ✅            │    │ Sleeps (no jobs)          │
└────────────┬───────────────┘    └────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────┐
│ STEP 6: Execute Scraper                                   │
│ scraper = registry.get_scraper("amazon")                 │
│ product = await scraper.get_product("B123456")           │
│                                                           │
│ INSIDE Scraper.get_product():                            │
│   1. Load anti-detection config                          │
│   2. Select random proxy from proxy_pool (health_score>70)
│   3. Create curl-cffi request with:                      │
│      - impersonate="chrome120"                           │
│      - Random User-Agent (desktop/mobile)                │
│      - Proxy rotation (change every 5 requests)          │
│   4. Make request to Amazon                              │
│   5. Parse HTML with CSS selectors:                      │
│      - title: "Sony WH-1000XM5 Wireless Headphones"    │
│      - price: "$348.99"                                  │
│      - stock: "In Stock"                                 │
│      - rating: "4.8 out of 5"                            │
│      - reviews: "2,345"                                  │
│      - images: ["img1.jpg", "img2.jpg", ...]           │
│   6. Return Product object                               │
└────────────┬───────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────┐
│ STEP 7: Save to Database                                 │
│ async with db.begin():                                   │
│   # INSERT or UPDATE Product                            │
│   stmt = insert(Product).values(                        │
│     asin="B123456",                                      │
│     supplier="amazon",                                   │
│     title="Sony WH-1000XM5...",                         │
│     price=348.99,                                        │
│     stock="In Stock",                                    │
│     ...                                                  │
│   ).on_conflict_do_update(...)                          │
│   result = await db.execute(stmt)                       │
│   product_id = result.inserted_primary_key[0]           │
│                                                           │
│   # INSERT Price History                                │
│   await db.execute(insert(PriceHistory).values(         │
│     product_id=product_id,                              │
│     old_price=329.99,  # from DB                        │
│     new_price=348.99,  # just scraped                   │
│     recorded_at=datetime.utcnow()                       │
│   ))                                                      │
│                                                           │
│   # COMMIT automatically at end of context              │
└────────────┬───────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────┐
│ STEP 8: Acknowledge Job & Update Status                  │
│ # Mark as processed in Redis                             │
│ await redis.xack("scraper:amazon", "scrapers", msg_id)  │
│                                                           │
│ # Update job status in DB                               │
│ await db.execute(                                        │
│   update(Job).where(Job.id == 789).values(              │
│     status="SUCCESS",                                    │
│     result={"product_id": 12345},                       │
│     completed_at=datetime.utcnow()                      │
│   )                                                       │
│ )                                                         │
└────────────┬───────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────┐
│ STEP 9: Publish Event (Pub/Sub)                         │
│ await redis.publish(                                     │
│   "product.changed",                                     │
│   json.dumps({                                           │
│     "type": "product.updated",                          │
│     "product_id": 12345,                                │
│     "change": {"price": 329.99 → 348.99},              │
│     "timestamp": datetime.utcnow()                      │
│   })                                                     │
│ )                                                        │
└────────────┬───────────────────────────────────────────┘
             │
      ┌──────┴────────────┐
      │                   │
      ▼                   ▼
┌────────────────┐  ┌──────────────────┐
│ policy_engine  │  │ notifications    │
│ listens to     │  │ service listens  │
│ event & runs:  │  │ to event &       │
│                │  │ sends alert to   │
│ IF price down  │  │ user if price    │
│ by 5%+ THEN    │  │ dropped >5%      │
│ - Queue check  │  │                  │
│ - Stock low?   │  │ "Price dropped!" │
│ - Margin OK?   │  │                  │
│ - Auto pause?  │  │                  │
└────────────────┘  └──────────────────┘
             │
      ┌──────┴────────────────────────┐
      │ Both update DB & publish new   │
      │ events if policies trigger     │
      ▼
    ✅ COMPLETE!
    
Total time: ~5-10 seconds from user request to completion!
User can check status: GET /jobs/789 → {"status": "SUCCESS"}
```

---

## 📊 DATABASE SCHEMA (15 Tables)

### Complete Table Definitions

```python
# TABLE 1: users
users:
  ├─ id (PK)
  ├─ email (UNIQUE)
  ├─ password_hash (bcrypt)
  ├─ first_name
  ├─ last_name
  ├─ tier (free, pro, enterprise)
  ├─ api_key (for integrations)
  ├─ created_at
  ├─ updated_at
  └─ is_active (soft delete)

# TABLE 2: sessions
sessions:
  ├─ id (PK)
  ├─ user_id (FK)
  ├─ token (JWT)
  ├─ refresh_token
  ├─ expires_at
  ├─ created_at
  └─ revoked_at (soft delete)

# TABLE 3: products
products:
  ├─ id (PK)
  ├─ supplier_id (FK)
  ├─ asin (or item_id, sku)
  ├─ title
  ├─ description
  ├─ price (decimal)
  ├─ stock (integer, can be "In Stock" text)
  ├─ rating (decimal 0-5)
  ├─ reviews_count
  ├─ images (JSONB array of URLs)
  ├─ url
  ├─ last_scraped_at
  ├─ created_at
  ├─ updated_at
  └─ is_archived

# TABLE 4: price_history
price_history:
  ├─ id (PK)
  ├─ product_id (FK)
  ├─ old_price (decimal)
  ├─ new_price (decimal)
  ├─ price_change_percent (decimal)
  ├─ recorded_at
  └─ reason (manual, scrape, api)

# TABLE 5: stock_history
stock_history:
  ├─ id (PK)
  ├─ product_id (FK)
  ├─ old_stock (integer)
  ├─ new_stock (integer)
  ├─ recorded_at
  └─ reason (scrape, api, manual)

# TABLE 6: suppliers
suppliers:
  ├─ id (PK)
  ├─ name (amazon, aliexpress, costco)
  ├─ base_url
  ├─ rate_limit (requests per minute)
  ├─ requires_js (bool, needs browser)
  ├─ scraper_config (JSONB, selectors, etc)
  ├─ is_active
  └─ created_at

# TABLE 7: store_accounts
store_accounts:
  ├─ id (PK)
  ├─ user_id (FK)
  ├─ marketplace (ebay, shopify, etsy)
  ├─ account_name
  ├─ api_key (encrypted)
  ├─ api_secret (encrypted)
  ├─ oauth_token (encrypted)
  ├─ oauth_refresh_token (encrypted)
  ├─ oauth_expires_at
  ├─ is_connected
  ├─ last_synced_at
  ├─ created_at
  └─ updated_at

# TABLE 8: listings
listings:
  ├─ id (PK)
  ├─ user_id (FK)
  ├─ product_id (FK)
  ├─ store_account_id (FK)
  ├─ external_listing_id (eBay item ID, Shopify product ID)
  ├─ title (can override product title)
  ├─ description
  ├─ price (current listing price)
  ├─ quantity_available
  ├─ status (Pending, Active, Paused, Ended, Delisted)
  ├─ status_reason (low_margin, manual_pause, out_of_stock)
  ├─ created_at
  ├─ updated_at
  └─ ended_at

# TABLE 9: marketplace_data
marketplace_data:
  ├─ id (PK)
  ├─ listing_id (FK)
  ├─ date (DATE, one record per day)
  ├─ views (integer)
  ├─ clicks (integer)
  ├─ sales (integer)
  ├─ revenue (decimal)
  ├─ cost_of_goods_sold (decimal)
  ├─ profit (calculated or stored)
  ├─ avg_rating_received (decimal)
  ├─ customer_feedbacks (integer)
  └─ notes

# TABLE 10: alerts
alerts:
  ├─ id (PK)
  ├─ user_id (FK)
  ├─ type (low_stock, low_margin, price_drop, policy_trigger)
  ├─ product_id (FK, nullable)
  ├─ listing_id (FK, nullable)
  ├─ severity (info, warning, critical)
  ├─ message
  ├─ data (JSONB, context data)
  ├─ is_read
  ├─ read_at
  ├─ created_at
  └─ acknowledged_at

# TABLE 11: jobs
jobs:
  ├─ id (PK)
  ├─ user_id (FK)
  ├─ type (scrape_amazon, track_products, sync_ebay, upload_shopify)
  ├─ status (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)
  ├─ params (JSONB, input data {asin, product_id, etc})
  ├─ result (JSONB, output {product_id, error, etc})
  ├─ error_message
  ├─ retry_count (0-3)
  ├─ created_at
  ├─ started_at
  ├─ completed_at
  └─ next_retry_at

# TABLE 12: proxy_pool
proxy_pool:
  ├─ id (PK)
  ├─ host (IP address)
  ├─ port (integer)
  ├─ username (nullable)
  ├─ password (nullable, encrypted)
  ├─ protocol (http, socks5)
  ├─ country
  ├─ health_score (0-100, updated by proxy_scorer)
  ├─ success_count (successful requests)
  ├─ failure_count (failed requests)
  ├─ last_checked_at
  ├─ last_failed_at
  ├─ is_active
  └─ created_at

# TABLE 13: analytics_cache
analytics_cache:
  ├─ id (PK)
  ├─ user_id (FK)
  ├─ metric_type (total_revenue, total_profit, top_products, etc)
  ├─ time_period (daily, weekly, monthly)
  ├─ data (JSONB, complex calculated data)
  ├─ computed_at
  ├─ expires_at (for TTL)
  └─ created_at

# TABLE 14: audit_log
audit_log:
  ├─ id (PK)
  ├─ user_id (FK)
  ├─ action (created, updated, deleted, paused, resumed)
  ├─ resource_type (product, listing, store_account)
  ├─ resource_id
  ├─ old_value (JSONB, what changed)
  ├─ new_value (JSONB, to what)
  ├─ ip_address
  ├─ user_agent
  ├─ timestamp
  └─ notes

# TABLE 15: notifications
notifications:
  ├─ id (PK)
  ├─ user_id (FK)
  ├─ type (alert, policy_trigger, job_complete, report)
  ├─ recipient (email, sms, webhook)
  ├─ subject
  ├─ body (JSONB or text)
  ├─ is_sent
  ├─ sent_at
  ├─ created_at
  └─ metadata (JSONB)
```

---

## 🔌 PLUGIN SYSTEMS

### Scraper Plugin Pattern

```python
# STEP 1: Define Base Class (scrapers/base.py)
class BaseScraper:
    async def get_product(self, id: str) -> Product:
        """Get single product"""
        raise NotImplementedError
    
    async def search(self, query: str) -> List[Product]:
        """Search products"""
        raise NotImplementedError

# STEP 2: Implement for Amazon (scrapers/amazon.py)
class AmazonScraper(BaseScraper):
    async def get_product(self, asin: str) -> Product:
        # Use curl-cffi with Chrome impersonation
        # Rotate proxies from proxy_pool
        # Handle rate limiting
        # Parse HTML with CSS selectors
        return Product(...)

# STEP 3: Register (scrapers/registry.py)
scrapers = {
    "amazon": AmazonScraper(),
    "aliexpress": AliExpressScraper(),
}

def get_scraper(name: str) -> BaseScraper:
    if name not in scrapers:
        raise ValueError(f"Unknown scraper: {name}")
    return scrapers[name]

# STEP 4: Use in Worker
scraper = get_scraper("amazon")
product = await scraper.get_product(asin)

# TO ADD NEW SCRAPER (e.g., Costco):
# 1. Create scrapers/costco.py
# 2. Class CostcoScraper(BaseScraper)
# 3. Implement get_product() and search()
# 4. Add to registry: scrapers["costco"] = CostcoScraper()
# ✅ NO changes to core code!
```

### Marketplace Plugin Pattern

```python
# STEP 1: Define Base Class (marketplaces/base.py)
class MarketplaceClient:
    async def create_listing(self, product: Product, price: float) -> str:
        """Create listing, return listing_id"""
        raise NotImplementedError
    
    async def update_price(self, listing_id: str, price: float) -> bool:
        """Update price"""
        raise NotImplementedError
    
    async def withdraw(self, listing_id: str) -> bool:
        """Remove listing"""
        raise NotImplementedError

# STEP 2: Implement for eBay (marketplaces/ebay.py)
class EBayClient(MarketplaceClient):
    async def create_listing(self, product, price) -> str:
        # Load OAuth2 token from store_account
        # Make API call to eBay Inventory API
        # createOffer() → publishOffer()
        # Return offerId
        return offering_id
    
    async def update_price(self, listing_id, price) -> bool:
        # Make API call to update price
        # Handle rate limiting (250/day)
        return True

# STEP 3: Register (marketplaces/registry.py)
marketplaces = {
    "ebay": EBayClient(),
    "shopify": ShopifyClient(),
}

def get_marketplace(name: str) -> MarketplaceClient:
    return marketplaces[name]

# STEP 4: Use in Worker
client = get_marketplace("ebay")
listing_id = await client.create_listing(product, price)

# TO ADD NEW MARKETPLACE (e.g., Shopify):
# 1. Create marketplaces/shopify.py
# 2. Class ShopifyClient(MarketplaceClient)
# 3. Implement create_listing(), update_price(), etc
# 4. Add to registry: marketplaces["shopify"] = ShopifyClient()
# ✅ NO changes to core code!
```

---

## 🔧 TECHNOLOGY STACK SPECIFICATIONS

### Python Ecosystem (3.11+)

```
Web Framework:
- FastAPI 0.109+ (async-first, auto-validation, Swagger)
- Uvicorn (ASGI server, 10+ workers)

Database:
- SQLAlchemy 2.0 (async ORM, type-safe)
- asyncpg 0.28+ (PostgreSQL async driver)
- PostgreSQL 15+ (production database)

Caching & Queues:
- redis.asyncio 5.0+ (async Redis client)
- Redis 7+ (Streams, Pub/Sub, Cache)

Data Validation:
- Pydantic v2 (request/response validation)
- Pydantic-settings (config management)

Authentication & Security:
- python-jose (JWT tokens)
- bcrypt (password hashing, 10+ rounds)
- passlib (password utilities)

Web Scraping & HTTP:
- curl-cffi 0.6+ (TLS fingerprint spoofing, Chrome impersonation)
- aiohttp (async HTTP client)

Testing:
- pytest (testing framework)
- pytest-asyncio (async test support)
- pytest-cov (coverage reporting)
- factoryboy (test fixtures)
- fakeredis (mock Redis for testing)

Development Tools:
- Black (code formatting)
- Flake8 (linting)
- mypy (type checking)
- pre-commit (git hooks)

Monitoring & Logging:
- structlog (structured JSON logging)
- prometheus-client (metrics)
- python-json-logger (JSON log format)

Deployment:
- Docker (containerization)
- Docker Compose (local development)
- Kubernetes (production orchestration)
- Gunicorn (WSGI server, production)
```

---

## 📋 COMPLETE BUILD ROADMAP (14 STEPS)

```
PHASE 1: CORE FOUNDATION (Days 1-2)
├─ STEP 1: config.py (Pydantic BaseSettings) ✅
├─ STEP 2: main.py (FastAPI app, minimal) ✅
├─ STEP 3A: core/database.py ✅ (SQLAlchemy async)
├─ STEP 3B: core/redis.py (Redis async)
├─ STEP 4A: core/security.py (JWT, bcrypt)
├─ STEP 4B: core/exceptions.py (Custom errors)
└─ STEP 4C: core/logging.py (Structured logging)

PHASE 2: DATA MODELS (Day 3)
├─ STEP 5A: models/base.py (Base ORM model)
├─ STEP 5B: models/user.py (User + Session models)
├─ STEP 5C: models/product.py (Product + History models)
├─ STEP 5D: models/listing.py (Listing + Marketplace models)
└─ STEP 5E: models/admin.py (Jobs, Alerts, etc)

PHASE 3: VALIDATION (Day 3)
├─ STEP 6A: schemas/user.py
├─ STEP 6B: schemas/product.py
├─ STEP 6C: schemas/listing.py
└─ STEP 6D: schemas/common.py

PHASE 4: API ROUTES (Day 4)
├─ STEP 7A: api/v1/router.py (API router setup)
├─ STEP 7B: api/v1/endpoints/auth.py (Login, signup, refresh)
├─ STEP 7C: api/v1/endpoints/products.py (CRUD + import)
├─ STEP 7D: api/v1/endpoints/listings.py (CRUD + upload)
├─ STEP 7E: api/v1/endpoints/stores.py (OAuth connect/disconnect)
└─ STEP 7F: api/v1/endpoints/analytics.py (Dashboard, trends)

PHASE 5: BUSINESS LOGIC (Day 5)
├─ STEP 8A: services/tracker_service.py (Parallel tracking)
├─ STEP 8B: services/policy_engine.py (Business rules)
├─ STEP 8C: services/analytics_service.py (Metrics calculation)
└─ STEP 8D: services/state_machine.py (Listing states)

PHASE 6: PLUGINS (Days 6-7)
├─ STEP 9A: scrapers/base.py (Abstract base)
├─ STEP 9B: scrapers/amazon.py (Amazon implementation)
├─ STEP 9C: scrapers/registry.py (Plugin discovery)
├─ STEP 9D: scrapers/anti_detect.py (TLS helpers)
├─ STEP 10A: marketplaces/base.py (Abstract base)
├─ STEP 10B: marketplaces/ebay.py (eBay implementation)
└─ STEP 10C: marketplaces/registry.py (Plugin discovery)

PHASE 7: WORKERS (Day 8)
├─ STEP 11A: workers/scraper_worker.py (Job processing)
├─ STEP 11B: workers/tracker_worker.py (Change detection)
└─ STEP 11C: workers/syncer_worker.py (Upload to marketplace)

PHASE 8: INFRASTRUCTURE (Days 9-10)
├─ STEP 12: tests/ (Unit, integration, E2E, fixtures)
├─ STEP 13: Dockerfile (Multi-stage container)
├─ STEP 14: docker-compose.yml (Local development)
└─ STEP 15: Deployment configs (Kubernetes, CI/CD)
```

---

## ⚠️ STRICT CODE QUALITY RULES

### EVERY FILE MUST HAVE:

```python
# 1. Type Hints (MANDATORY)
async def get_products(
    user_id: int,
    limit: int = 10,
    offset: int = 0
) -> List[ProductSchema]:
    """Get products for user with pagination."""
    # NOT: async def get_products(user_id, limit=10):

# 2. Docstrings (MANDATORY)
async def track_product(product_id: int) -> bool:
    """
    Track product price and stock changes.
    
    Args:
        product_id: Product ID to track
    
    Returns:
        bool: True if changes detected, False otherwise
    
    Raises:
        ProductNotFound: If product doesn't exist
    """

# 3. Error Handling (MANDATORY)
try:
    result = await scraper.get_product(asin)
except Exception as e:
    logger.error("Scrape failed", asin=asin, error=str(e))
    # NOT: except: pass

# 4. Async/Await (NO SYNC CODE ALLOWED)
# ✅ GOOD:
product = await db.execute(select(Product).where(...))

# ❌ BAD:
product = db.query(Product).filter(...).first()

# 5. Logging (MANDATORY)
logger.info("product_imported", product_id=123, asin="B123", user_id=456)
# NOT: print("Product imported")

# 6. Pydantic Validation (MANDATORY)
class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asin: str
    price: Decimal
    title: str

# 7. SQLAlchemy selectinload (NO N+1 QUERIES)
stmt = select(Product).options(
    selectinload(Product.listings),
    selectinload(Product.price_history)
)
# NOT: for product in products: product.listings (triggers N queries)

# 8. Transaction Management (DATA INTEGRITY)
async with db.begin():
    await db.execute(insert(Product).values(...))
    await db.execute(insert(PriceHistory).values(...))
    # Auto-commits on success, rolls back on error

# 9. No Hardcoded Values (ALWAYS USE CONFIG)
# ✅ GOOD:
api_key = settings.EBAY_API_KEY

# ❌ BAD:
api_key = "sk-12345"

# 10. Comments for Complex Logic (ONLY)
# ✅ GOOD - complex logic gets comment:
# Calculate price with 20% margin and 2.9% + $0.30 fee
price_with_margin = (cost / 0.8) + (cost / 0.8 * 0.029) + 0.30

# ❌ BAD - obvious code gets comment:
# Increment counter by 1
counter += 1
```

---
