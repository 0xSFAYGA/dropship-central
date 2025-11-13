# STEP 4A: Generate security.py

## Instructions
1. Open Gemini CLI: `gemini`
2. First ask Gemini to read GEMINI-MASTER.md
3. Copy the EXACT prompt below
4. Paste into Gemini
5. Copy generated code
6. Save to: `backend/app/core/security.py`
7. Run: `python3 -m py_compile backend/app/core/security.py`
8. Commit: `git add backend/app/core/security.py && git commit -m "feat(security): add JWT and bcrypt authentication utilities"`

---

FIRST MESSAGE:

Read and understand GEMINI-MASTER.md file in project root, especially:
- Code quality rules section
- Plugin systems section
- Database schema

Confirm when ready.

---

THEN PASTE THIS:

---

STEP 4A: Create backend/app/core/security.py

ROLE: JWT token and password authentication utilities
LOCATION: Core module, imported by routes and dependencies
DEPENDS ON: python-jose, bcrypt, config.py
PROVIDES: Password hashing, JWT creation/validation functions

ARCHITECTURE CONTEXT:
- Used by: auth routes (STEP 7B), get_current_user dependency
- Provides: Security functions for entire application
- No FastAPI code here - pure utilities

⚠️ CONSTRAINTS:
- Do NOT import FastAPI
- Do NOT create routes
- Do NOT import database models
- ONLY authentication utilities

✅ DO INCLUDE:
1. Imports:
   - from jose import JWTError, jwt
   - from passlib.context import CryptContext
   - from datetime import datetime, timedelta, timezone
   - from config import get_settings
   - import logging
   - from typing import Optional

2. Password hashing:
   - pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   - Function hash_password(password: str) -> str
     • Use bcrypt with 12 rounds
     • Return hashed password
   - Function verify_password(plain: str, hashed: str) -> bool
     • Compare plain text with hash
     • Return True/False

3. JWT Token creation:
   - Function create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str
     • Load SECRET_KEY and ALGORITHM from config
     • Add exp claim (expiry time)
     • Default expiry: ACCESS_TOKEN_EXPIRE_MINUTES from config
     • Return JWT token string
   
   - Function create_refresh_token(data: dict) -> str
     • Similar to access token
     • Longer expiry: REFRESH_TOKEN_EXPIRE_DAYS from config
     • Return JWT token string

4. JWT Token validation:
   - Function decode_token(token: str) -> dict
     • Load SECRET_KEY and ALGORITHM from config
     • Decode JWT with jwt.decode()
     • Handle JWTError, ValidationError
     • Return payload dict
   
   - Function get_token_exp(token: str) -> datetime
     • Decode token
     • Extract exp claim
     • Return datetime

5. Helper functions:
   - Function verify_token(token: str) -> bool
     • Try to decode
     • Return True if valid, False if expired/invalid

Include:
- Type hints on all functions
- Docstrings (Google style)
- Error handling with try/except
- Logging: log token creation, validation failures
- Comments explaining JWT flow

❌ DO NOT INCLUDE:
- FastAPI routes
- Database queries
- Dependency functions (Depends)
- Any business logic
- Rate limiting

Make it production-ready security module.

---
