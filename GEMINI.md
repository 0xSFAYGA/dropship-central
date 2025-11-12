# Dropship Central - MVP Backend

## Project Overview
Multi-marketplace dropshipping automation SaaS backend.
Building extensible, production-ready system.

## Tech Stack (2025)
- FastAPI 0.109+
- SQLAlchemy 2.0 async
- PostgreSQL 15
- Redis 7
- curl-cffi 0.6+ (anti-detection)
- Pydantic v2
- Python 3.11+

## Architecture (Extensible)
- Plugin-based scrapers (Amazon ready, AliExpress template)
- Plugin-based marketplaces (eBay ready, Shopify template)
- Async services (tracker, policy engine, analytics)
- Redis Streams job queues
- Event-driven design

## Code Patterns to Reuse
1. amazon_poller.py - curl-cffi + Chrome + proxies
2. multi_asin_driver.py - Parallel asyncio tasks
3. proxy_scorer.py - Health management

## Database (15 Tables)
users, sessions, products, price_history, stock_history, suppliers, store_accounts, listings, marketplace_data, alerts, jobs, proxy_pool, analytics_cache, audit_log, notifications

## Code Style (STRICT)
- Async/await everywhere
- Type hints on all functions
- Pydantic v2 ConfigDict(from_attributes=True)
- SQLAlchemy selectinload() for relationships
- Structured JSON logging
- Custom exceptions
- Prometheus metrics

## Testing
- Unit: Isolated components
- Integration: DB + Redis
- E2E: Full workflows
- Coverage: 80%+ minimum

## Git Workflow
- main: production (protected)
- staging: pre-prod (protected)
- develop: integration (unprotected)
- feature/*: individual features
