# STEP 4B: Generate exceptions.py

## Instructions
1. Open Gemini CLI: `gemini`
2. Copy the prompt below
3. Paste into Gemini
4. Copy generated code
5. Save to: `backend/app/core/exceptions.py`
6. Commit: `git add backend/app/core/exceptions.py && git commit -m "feat(exceptions): add custom exception classes"`

---

PASTE THIS INTO GEMINI:

---

STEP 4B: Create backend/app/core/exceptions.py

ROLE: Custom application exception classes
LOCATION: Core module, imported by routes and services
DEPENDS ON: FastAPI HTTPException type hints only
PROVIDES: Exception classes for entire application

ARCHITECTURE CONTEXT:
- Used by: All routes, services, workers
- Each exception maps to HTTP status code
- Will have exception handlers in main.py (later)

⚠️ CONSTRAINTS:
- ONLY exception class definitions
- Do NOT create exception handlers
- Do NOT import database models
- Do NOT create FastAPI routes

✅ DO INCLUDE:
1. Base custom exception class:
   - class AppException(Exception)
   - Attributes: status_code (int), detail (str), error_code (str)

2. Authentication exceptions:
   - InvalidCredentials (401)
   - TokenExpired (401)
   - TokenInvalid (401)
   - UserNotActive (403)

3. Resource not found exceptions:
   - ProductNotFound (404)
   - ListingNotFound (404)
   - StoreAccountNotFound (404)
   - UserNotFound (404)

4. Business logic exceptions:
   - RateLimitExceeded (429)
   - LowMargin (400)
   - OutOfStock (400)
   - ListingAlreadyExists (400)
   - InvalidListingState (400)

5. External API exceptions:
   - ExternalAPIError (500, base for external failures)
   - EBayAPIError (external)
   - AmazonScrapingError (external)
   - ProxyConnectionError (external)

6. For each exception:
   - Class attributes: status_code, error_code
   - __init__(self, detail: str, **kwargs)
   - Store extra context in self.context dict
   - String representation

Include:
- Type hints on all methods
- Docstrings explaining when to raise
- Comments for each category
- Error code constants (e.g., "INVALID_CREDENTIALS")

❌ DO NOT INCLUDE:
- Exception handlers (those go in main.py)
- FastAPI HTTPException wrapping (not here)
- Routes or endpoints
- Database code
- Business logic

Make it clean exception hierarchy.

---
