cd ~/projects/dropship-central

cat > GEMINI.md << 'EOF'
# Dropship Central - MVP Backend (Production-Ready)

## Project Status
Building extensible dropshipping automation SaaS backend.
Started: Nov 12, 2025. Target: MVP in 10 days.

## Tech Stack (2025)
- FastAPI 0.109+ (async, DI)
- SQLAlchemy 2.0 (async, selectinload)
- PostgreSQL 15 (asyncpg)
- Redis 7 (Streams, Pub/Sub)
- curl-cffi 0.6+ (Chrome impersonation, TLS spoofing)
- Pydantic v2 (validation)
- pytest-asyncio (testing)
- Python 3.11+

## Architecture (Plugin-Based, Extensible)

### Scrapers (Plugin System)
- **Base**: scrapers/base.py (abstract BaseScraper)
- **Implemented**: amazon.py (curl-cffi + proxy rotation from amazon_poller.py)
- **Template**: aliexpress_template.py (ready for implementation)
- **Registry**: scrapers/registry.py (self-discovers scrapers)
- **Future**: Add new scraper = 1 file + register

### Marketplaces (Plugin System)
- **Base**: marketplaces/base.py (abstract MarketplaceClient)
- **Implemented**: ebay.py (Inventory API, OAuth2)
- **Template**: shopify_template.py (ready for implementation)
- **Registry**: marketplaces/registry.py (self-discovers marketplaces)
- **Future**: Add new marketplace = 1 file + register

### Workers (Redis Streams Consumers)
- **scraper_worker**: Consumes "scraper:amazon" jobs
- **tracker_worker**: Consumes "tracker:all" jobs
- **syncer_worker**: Consumes "syncer:ebay" jobs

### Services (Business Logic)
- **tracker_service**: Parallel price/stock monitoring (async tasks)
- **policy_engine**: Low-stock, margin, price-drop rules
- **analytics_service**: Revenue, profit, trends
- **state_machine**: Listing lifecycle states

## Your Existing Code Patterns (REUSE)
1. amazon_poller.py → Use curl-cffi + Chrome + proxies pattern
2. multi_asin_driver.py → Use parallel asyncio tasks pattern
3. proxy_scorer.py → Use health management pattern

## Database Schema (15 Tables - Extensible)
users, sessions, products, price_history, stock_history, suppliers, store_accounts, listings, marketplace_data, alerts, jobs, proxy_pool, analytics_cache, audit_log, notifications

## MVP Features (10 Days)
- Day 1-2: Core Foundation (config, main, models, schemas)
- Day 3-4: Plugin Architecture (scrapers, marketplaces registries)
- Day 5: Tracking & Policies (tracker, policy engine)
- Day 6: Event Bus (Redis Streams, workers)
- Day 7: API Endpoints (REST routes)
- Day 8: Testing (unit, integration, e2e)
- Day 9: Docker (Dockerfile, docker-compose)
- Day 10: Docs & Release

## Code Style Rules (STRICT)
- Async/await everywhere (no blocking I/O)
- Type hints on EVERY function parameter and return
- Pydantic v2 with ConfigDict(from_attributes=True)
- SQLAlchemy selectinload() for relationships (NO N+1 queries)
- Custom exceptions with proper HTTP status
- Structured JSON logging (request_id, user_id, duration_ms)
- Prometheus metrics on critical paths
- Error handling: try/except with retry logic
- Tests: Unit, integration, E2E (80%+ coverage)

## ⚠️ PROMPT STRUCTURE RULES (FOR GEMINI CLI)

### Rule 1: Single Responsibility Per Step
Each step creates ONE focused module/feature.
- ❌ Do NOT add other modules in same step
- ✅ Database goes in Step 3 ONLY
- ✅ Redis goes in Step 4 ONLY
- ✅ FastAPI app goes in Step 2 ONLY

### Rule 2: Explicit Constraints
Every prompt MUST include:
- ⚠️ CONSTRAINTS section listing what NOT to do
- ✅ DO INCLUDE section with required features
- ❌ DO NOT INCLUDE section with forbidden items

### Rule 3: No Module Cross-Contamination
- ❌ Do NOT import modules from other steps in same file
- ❌ Do NOT initialize services not related to this step
- ✅ Each file handles ONE clear responsibility

### Rule 4: Minimal, Focused Code
- ❌ Do NOT add "nice-to-have" features
- ❌ Do NOT add error handling beyond scope
- ✅ Generate ONLY what's requested
- ✅ Keep files <150 lines when possible

### Rule 5: Explicit Dependencies
- ❌ Do NOT assume other modules exist
- ✅ Clearly state imports needed
- ✅ State which functions this module calls (if any)

## Step-by-Step Prompts (Copy Exact)

### STEP 1: Config (✅ DONE)
