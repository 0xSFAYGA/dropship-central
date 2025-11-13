# STEP 5: Generate Database Models

## Instructions
1. Open Gemini CLI: `gemini`
2. Copy the prompt below
3. Paste into Gemini
4. Copy generated code
5. Save to: `backend/app/models/__init__.py`
6. Commit: `git add backend/app/models/ && git commit -m "feat(models): add all 15 SQLAlchemy ORM models"`

---

PASTE THIS INTO GEMINI:

---

STEP 5: Create backend/app/models/__init__.py (All 15 ORM Models)

ROLE: SQLAlchemy 2.0 ORM model definitions for database schema
LOCATION: Models package, imported by routes and services
DEPENDS ON: SQLAlchemy 2.0, config.py
PROVIDES: 15 database models

ARCHITECTURE CONTEXT:
- Used by: Database module (get_async_session), routes, services
- Defines: Complete database schema as Python classes
- Maps to: 15 PostgreSQL tables (see GEMINI-MASTER.md)

⚠️ CONSTRAINTS:
- ONLY model definitions
- Do NOT create database initialization code
- Do NOT create routes
- Do NOT import database connection code
- ONLY SQLAlchemy models

✅ DO INCLUDE ALL 15 MODELS:

1. **User** (Authentication)
   - id (PK, Integer)
   - email (String UNIQUE)
   - password_hash (String)
   - first_name, last_name
   - tier (Enum: free, pro, enterprise)
   - api_key (String, generated)
   - created_at, updated_at (DateTime with timezone)
   - is_active (Boolean, soft delete)
   - Relationships: sessions, products, store_accounts, listings, alerts

2. **Session** (Auth Tokens)
   - id (PK, Integer)
   - user_id (FK)
   - token (String, JWT)
   - refresh_token (String)
   - expires_at (DateTime)
   - created_at
   - revoked_at (nullable, soft delete)

3. **Product** (Scraped Data)
   - id (PK, Integer)
   - supplier_id (FK)
   - asin (String UNIQUE per supplier)
   - title (String)
   - description (Text)
   - price (Numeric)
   - stock (String or Integer)
   - rating (Numeric 0-5)
   - reviews_count (Integer)
   - images (JSONB array)
   - url (String)
   - last_scraped_at (DateTime)
   - created_at, updated_at
   - is_archived (Boolean)
   - Indexes: (supplier_id, asin), last_scraped_at
   - Relationships: price_history, stock_history, listings

4. **PriceHistory** (Tracking Changes)
   - id (PK, Integer)
   - product_id (FK)
   - old_price (Numeric)
   - new_price (Numeric)
   - price_change_percent (Numeric, calculated)
   - recorded_at (DateTime)
   - reason (Enum: manual, scrape, api)

5. **StockHistory** (Tracking Changes)
   - id (PK, Integer)
   - product_id (FK)
   - old_stock (Integer)
   - new_stock (Integer)
   - recorded_at (DateTime)
   - reason (Enum: scrape, api, manual)

6. **Supplier** (Scraper Config)
   - id (PK, Integer)
   - name (String UNIQUE: amazon, aliexpress, costco)
   - base_url (String)
   - rate_limit (Integer, req/min)
   - requires_js (Boolean)
   - scraper_config (JSONB, CSS selectors, etc)
   - is_active (Boolean)
   - created_at

7. **StoreAccount** (Marketplace Credentials)
   - id (PK, Integer)
   - user_id (FK)
   - marketplace (String: ebay, shopify, etsy)
   - account_name (String)
   - api_key (String, encrypted)
   - api_secret (String, encrypted)
   - oauth_token (String, encrypted)
   - oauth_refresh_token (String, encrypted)
   - oauth_expires_at (DateTime, nullable)
   - is_connected (Boolean)
   - last_synced_at (DateTime, nullable)
   - created_at, updated_at
   - Indexes: (user_id, marketplace)
   - Relationships: listings

8. **Listing** (Product Listings on Marketplaces)
   - id (PK, Integer)
   - user_id (FK)
   - product_id (FK)
   - store_account_id (FK)
   - external_listing_id (String: eBay item ID, etc)
   - title (String)
   - description (Text)
   - price (Numeric)
   - quantity_available (Integer)
   - status (Enum: Pending, Active, Paused, Ended, Delisted)
   - status_reason (String: low_margin, manual_pause, etc)
   - created_at, updated_at
   - ended_at (DateTime, nullable)
   - Indexes: (user_id, product_id, store_account_id), status
   - Relationships: marketplace_data

9. **MarketplaceData** (Daily Performance)
   - id (PK, Integer)
   - listing_id (FK)
   - date (Date, one per day)
   - views (Integer)
   - clicks (Integer)
   - sales (Integer)
   - revenue (Numeric)
   - cost_of_goods_sold (Numeric)
   - profit (Numeric)
   - avg_rating_received (Numeric)
   - customer_feedbacks (Integer)
   - notes (Text, nullable)

10. **Alert** (Notifications)
    - id (PK, Integer)
    - user_id (FK)
    - type (Enum: low_stock, low_margin, price_drop, policy_trigger)
    - product_id (FK, nullable)
    - listing_id (FK, nullable)
    - severity (Enum: info, warning, critical)
    - message (Text)
    - data (JSONB, context)
    - is_read (Boolean)
    - read_at (DateTime, nullable)
    - created_at
    - acknowledged_at (DateTime, nullable)

11. **Job** (Background Tasks)
    - id (PK, Integer)
    - user_id (FK)
    - type (String: scrape_amazon, track_products, sync_ebay)
    - status (Enum: PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)
    - params (JSONB, input data)
    - result (JSONB, output data)
    - error_message (Text, nullable)
    - retry_count (Integer, 0-3)
    - created_at, started_at, completed_at
    - next_retry_at (DateTime, nullable)
    - Indexes: (user_id, status, type), created_at

12. **ProxyPool** (Proxy Management)
    - id (PK, Integer)
    - host (String)
    - port (Integer)
    - username (String, nullable)
    - password (String, nullable, encrypted)
    - protocol (String: http, socks5)
    - country (String)
    - health_score (Integer 0-100)
    - success_count (Integer)
    - failure_count (Integer)
    - last_checked_at (DateTime)
    - last_failed_at (DateTime, nullable)
    - is_active (Boolean)
    - created_at
    - Indexes: is_active, health_score

13. **AnalyticsCache** (Cached Metrics)
    - id (PK, Integer)
    - user_id (FK)
    - metric_type (String: total_revenue, total_profit, top_products)
    - time_period (String: daily, weekly, monthly)
    - data (JSONB, complex calculated data)
    - computed_at (DateTime)
    - expires_at (DateTime, TTL)
    - created_at

14. **AuditLog** (Activity Tracking)
    - id (PK, Integer)
    - user_id (FK)
    - action (String: created, updated, deleted, paused, resumed)
    - resource_type (String: product, listing, store_account)
    - resource_id (Integer)
    - old_value (JSONB, what changed)
    - new_value (JSONB, to what)
    - ip_address (String)
    - user_agent (String)
    - timestamp (DateTime)
    - notes (Text, nullable)

15. **Notification** (User Messages)
    - id (PK, Integer)
    - user_id (FK)
    - type (String: alert, policy_trigger, job_complete, report)
    - recipient (String: email, sms, webhook)
    - subject (String)
    - body (Text)
    - is_sent (Boolean)
    - sent_at (DateTime, nullable)
    - created_at
    - metadata (JSONB, nullable)

GENERAL REQUIREMENTS FOR ALL MODELS:
- Use SQLAlchemy 2.0 ORM style
- Inherit from: DeclarativeBase (defined once)
- All have: id (PK), created_at (default now), updated_at (onupdate now)
- Type hints: all columns typed
- Relationships: back_populates for bidirectional
- Indexes: on FKs and common filters
- Validators: where needed (email format, enums, etc)
- Timestamps: datetime with timezone aware
- Soft deletes: is_archived, revoked_at columns
- Encrypted fields: use encrypted_password hybrid property

Include:
- Type hints on all attributes
- Docstrings for each model (what it represents)
- Comments for important relationships
- __tablename__ explicit
- __repr__ for debugging

❌ DO NOT INCLUDE:
- Database initialization code
- Session management code
- Query logic (that goes in repositories)
- Routes or endpoints
- Service logic

Make it clean, well-organized, production-ready schema.

---
