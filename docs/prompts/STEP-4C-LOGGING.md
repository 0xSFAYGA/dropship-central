# STEP 4C: Generate logging.py

## Instructions
1. Open Gemini CLI: `gemini`
2. Copy the prompt below
3. Paste into Gemini
4. Copy generated code
5. Save to: `backend/app/core/logging.py`
6. Commit: `git add backend/app/core/logging.py && git commit -m "feat(logging): add structured JSON logging setup"`

---

PASTE THIS INTO GEMINI:

---

STEP 4C: Create backend/app/core/logging.py

ROLE: Structured JSON logging configuration
LOCATION: Core module, imported by main.py for setup
DEPENDS ON: structlog, logging, config.py
PROVIDES: Configured logger for entire application

ARCHITECTURE CONTEXT:
- Used by: main.py (setup in lifespan), all modules (get logger)
- Provides: Structured JSON logs for production
- Machine-parseable for ELK/Datadog ingestion

⚠️ CONSTRAINTS:
- ONLY logging configuration
- Do NOT create routes or endpoints
- Do NOT import database models
- Do NOT import FastAPI app

✅ DO INCLUDE:
1. structlog configuration:
   - Configure for JSON output in production
   - Human-readable format in development
   - Timestamps, log levels, logger names

2. Sensitive data redaction:
   - Redact: passwords, tokens, api_keys, secrets
   - Redact patterns: *_secret, *_password, *_token
   - Redact request bodies with sensitive data

3. Request context tracking:
   - request_id (unique per request)
   - user_id (who made request)
   - duration_ms (how long operation took)
   - status_code (HTTP response code)

4. Function setup_logging(log_level: str, is_production: bool = False):
   - Called by main.py on startup
   - Configure structlog with handlers
   - Set JSON formatter for production
   - Set human-readable formatter for dev
   - Return configured logger

5. Function get_logger(name: str):
   - Returns structlog logger for module
   - Usage: logger = get_logger(__name__)

6. Context managers/helpers:
   - Function log_operation(operation_name: str, **context):
     • Context manager for timed operations
     • Logs start, duration, any errors
     • Auto-captures duration_ms

Include:
- Type hints on all functions
- Docstrings
- Comments explaining structlog setup
- Production vs development differences
- Field names: timestamp, level, logger, message, request_id, user_id, duration_ms

❌ DO NOT INCLUDE:
- Routes or endpoints
- Database code
- Business logic
- Exception handlers

Make it production-ready logging system.

---
