# STEP 6: Generate Pydantic Schemas

## Instructions
1. Open Gemini CLI: `gemini`
2. Copy the prompt below
3. Paste into Gemini
4. Copy generated code
5. Save to: `backend/app/schemas/__init__.py`
6. Commit: `git add backend/app/schemas/ && git commit -m "feat(schemas): add Pydantic v2 validation schemas"`

---

PASTE THIS INTO GEMINI:

---

STEP 6: Create backend/app/schemas/__init__.py (Pydantic Schemas)

ROLE: Pydantic v2 request/response validation schemas
LOCATION: Schemas package, imported by routes
DEPENDS ON: Pydantic v2, models
PROVIDES: Request/response validation

ARCHITECTURE CONTEXT:
- Used by: All API routes for validation
- Provides: Type-safe request/response handling
- Maps to: Database models (see models/__init__.py)

⚠️ CONSTRAINTS:
- ONLY Pydantic model definitions
- Do NOT create validation logic beyond Pydantic
- Do NOT import FastAPI
- Do NOT create routes

✅ DO INCLUDE SCHEMAS FOR ALL KEY MODELS:

1. **User Schemas**:
   - UserSchema (response, all fields)
   - UserCreateSchema (request, email + password only)
   - UserUpdateSchema (request, optional fields)

2. **Product Schemas**:
   - ProductSchema (response, all fields including metadata)
   - ProductCreateSchema (request, supplier + asin)
   - ProductDetailSchema (response, includes relationships)

3. **Listing Schemas**:
   - ListingSchema (response)
   - ListingCreateSchema (request, product_id + store_account_id + price)
   - ListingUpdateSchema (request, price + quantity_available)

4. **StoreAccount Schemas**:
   - StoreAccountSchema (response, no secrets)
   - StoreAccountCreateSchema (request, marketplace + credentials)

5. **Price/Stock History Schemas**:
   - PriceHistorySchema (response)
   - StockHistorySchema (response)

6. **Alert Schemas**:
   - AlertSchema (response)

7. **Job Schemas**:
   - JobSchema (response, all fields)
   - JobCreateSchema (request, type + params)

8. **Analytics Schemas**:
   - AnalyticsSchema (response, dashboard data)

SCHEMA REQUIREMENTS:
- Use Pydantic v2 BaseModel
- ConfigDict(from_attributes=True) for ORM conversion
- Type hints: all fields typed
- Field descriptions: for Swagger docs
- Example values: show in Swagger
- Validators: email format, enums, etc
- ISO datetime strings (not Python datetime objects)

RESPONSES SHOULD NOT INCLUDE:
- Passwords
- API tokens
- Secret keys
- Encrypted credentials

Include:
- Docstrings for each schema
- Field descriptions
- Example values for testing
- Validators for data format
- Relationships in DetailSchema (for nested responses)

❌ DO NOT INCLUDE:
- Business logic
- Database queries
- Routes or endpoints
- Authentication logic

Make it complete validation layer.

---
