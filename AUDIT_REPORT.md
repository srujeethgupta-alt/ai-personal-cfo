# AI Personal CFO — Production Audit Report
## Date: 2025-06-17
## Auditor: Principal Architect + Security + DevOps + QA

---

## EXECUTIVE SUMMARY

**Overall Readiness Score: 62/100**

The project has a solid foundation with modular backend architecture, JWT auth, multi-user support, AI tool calling, and a premium frontend. However, **critical deployment blockers, security gaps, and API inconsistencies** must be resolved before production deployment.

| Category | Score | Status |
|----------|-------|--------|
| Architecture | 75 | Good |
| Authentication | 70 | Good with gaps |
| Security | 45 | Needs work |
| Database | 65 | Acceptable |
| API Layer | 60 | Inconsistent |
| AI System | 65 | Functional |
| Frontend | 70 | Good |
| Deployment | 20 | Critical gaps |
| Performance | 55 | Needs optimization |
| QA / Testing | 30 | No test suite |

---

## PHASE 1: FULL PROJECT AUDIT

### 1.1 BACKEND — CRITICAL FINDINGS

#### CRITICAL-1: `users` router imported but NEVER included in FastAPI app
**File:** `backend/main.py:12`  
**Severity:** CRITICAL  
**Root Cause:** `main.py` imports `users` from `routers` but never calls `app.include_router(users.router)`. The `users.py` router has endpoints like `POST /api/users` (add user), `GET /api/users` (list all), etc., but they are unreachable.  
**Risk:** Admin user management API is completely dead.  
**Fix:** Add `app.include_router(users.router)` in `main.py`.

#### CRITICAL-2: Password hashing mismatch — `requirements.txt` says bcrypt, code uses pbkdf2_sha256
**File:** `backend/auth.py:21` vs `backend/requirements.txt:20`  
**Severity:** CRITICAL  
**Root Cause:** `requirements.txt` installs `passlib[bcrypt]` but `auth.py` configures `CryptContext(schemes=["pbkdf2_sha256"])`. The bcrypt dependency is unused. Worse, if someone reads requirements.txt and expects bcrypt, they get a different algorithm.  
**Risk:** Password hashing does not match documented requirements. Security expectation mismatch.  
**Fix:** Change `auth.py` to `CryptContext(schemes=["bcrypt"], deprecated="auto")` to match `requirements.txt`.

#### CRITICAL-3: `main.py` runs migrations AND admin seed on every import
**File:** `backend/main.py:26-27, 62`  
**Severity:** CRITICAL  
**Root Cause:** `run_migrations()` and `seed_default_admin()` execute at module import time (global scope). Every time `main.py` is imported (e.g., by uvicorn, by tests, by CLI tools), these run. This is fine for a one-shot but problematic for:  
- Running tests (migrations run during test discovery)
- Multiple workers (race conditions)
- `seed_default_admin()` logs the admin password to the console every single startup  
**Risk:** Password leak in logs, race conditions on startup, slow cold starts.  
**Fix:** Wrap `run_migrations()` and `seed_default_admin()` in a `if __name__ == "__main__":` block or use a startup event handler.

#### CRITICAL-4: `agent_tools.py` functions receive `db` as a parameter but `ai.py` injects it incorrectly
**File:** `backend/routers/ai.py:115-125`  
**Severity:** CRITICAL  
**Root Cause:** `_execute_tool` does:
```python
parameters["user_id"] = user_id
parameters["db"] = db
result = func(**parameters)
```
But `agent_tools.py` functions like `create_expense` are defined as:
```python
def create_expense(db, user_id, category, amount, expense_date, notes):
```
The `db` parameter is injected as a keyword argument. If `parameters` already contains a `db` key (which it shouldn't, but users could send malicious JSON), this would override the real session. More importantly, the `db` object is a SQLAlchemy Session that is being passed into the AI tool function — this is architecturally correct but fragile.  
**Risk:** Session management issues, potential for SQL injection if user-controlled JSON reaches raw SQL.  
**Fix:** Use a dedicated `execute_tool` wrapper that validates parameters and passes `db` and `user_id` explicitly, not via the JSON payload.

#### CRITICAL-5: `ai.py` streaming endpoint does NOT support tool execution
**File:** `backend/routers/ai.py:260+`  
**Severity:** CRITICAL  
**Root Cause:** The streaming `ask_cfo_stream` endpoint uses the same prompt as the regular endpoint but does NOT implement `_extract_tool_call` or `_execute_tool`. The AI could still output `TOOL_CALL:` but the streaming endpoint would stream it as raw text to the user, which is confusing and broken.  
**Risk:** Broken streaming UX for action requests.  
**Fix:** Disable tool execution for streaming or implement a two-pass streaming flow (complex).

#### HIGH-1: `main.py` CORS `allow_origin_regex` may not work as expected
**File:** `backend/main.py:77`  
**Severity:** HIGH  
**Root Cause:** The CORS config uses `allow_origin_regex=r"(http://.*:5173|https://.*\.loca\.lt)"`. Starlette's CORS middleware documentation says `allow_origin_regex` is supported, but the regex `http://.*:5173` is too broad — it matches ANY host with port 5173. Also, `allow_credentials=True` with `allow_origin_regex` can cause browser issues.  
**Risk:** CORS preflight failures, security exposure.  
**Fix:** Use explicit `allow_origins` list with environment-driven configuration.

#### HIGH-2: `requirements.txt` has duplicate/conflicting `dotenv` packages
**File:** `backend/requirements.txt:8,18`  
**Severity:** HIGH  
**Root Cause:** Both `dotenv==0.9.9` and `python-dotenv==1.1.0` are listed. `dotenv` is a different package that conflicts with `python-dotenv`. The code uses `python-dotenv` (`from dotenv import load_dotenv`).  
**Risk:** Package conflicts, import errors.  
**Fix:** Remove `dotenv==0.9.9`.

#### HIGH-3: `users.py` router lacks auth protection — anyone can list all users
**File:** `backend/routers/users.py`  
**Severity:** HIGH  
**Root Cause:** The `users.py` router has endpoints like `GET /api/users` that return all users with no authentication. It does not use `get_current_user` or any admin check.  
**Risk:** Data leak — any unauthenticated user can enumerate all registered users.  
**Fix:** Add `get_current_user` dependency and admin check middleware.

#### HIGH-4: No rate limiting on any endpoint
**File:** All routers  
**Severity:** HIGH  
**Root Cause:** No rate limiter (e.g., slowapi, fastapi-limiter) is installed or configured. Brute force on login, password reset, and AI endpoints is possible.  
**Risk:** Brute force attacks, AI API cost exhaustion.  
**Fix:** Install `slowapi` and add rate limits to auth and AI endpoints.

#### HIGH-5: No input sanitization before AI prompts
**File:** `backend/routers/ai.py`  
**Severity:** HIGH  
**Root Cause:** User questions are passed directly into the AI prompt without sanitization. While Groq's API is generally safe, a malicious user could craft a prompt injection attack to extract other users' data or manipulate the AI.  
**Risk:** Prompt injection, data leakage via AI.  
**Fix:** Add prompt injection detection and strip suspicious patterns.

#### HIGH-6: `get_or_create_user` in analytics_service still creates a default user with ID 1
**File:** `backend/services/analytics_service.py:14-23`  
**Severity:** HIGH  
**Root Cause:** `get_or_create_user(db, user_id=1)` creates a hardcoded user if none exists. In a multi-user system, this is dangerous because calling `get_or_create_user(db, user_id=1)` could create a "Default User" that then receives all orphaned data.  
**Risk:** Data pollution, phantom user creation.  
**Fix:** Remove `get_or_create_user` entirely. All endpoints require `current_user`, so a user always exists.

#### HIGH-7: `agent_tools.py` `_verify_ownership` returns None instead of raising an error
**File:** `backend/services/agent_tools.py:49-50`  
**Severity:** HIGH  
**Root Cause:** `_verify_ownership` returns `None` if the record doesn't belong to the user, but the calling functions don't always check this. For example, `update_expense` does check it, but the pattern is inconsistent.  
**Risk:** Some tool functions might allow cross-user modification.  
**Fix:** Make `_verify_ownership` raise an explicit exception.

#### HIGH-8: `frontend/src/services/api.js` uses `window.location.hostname` for API base URL
**File:** `frontend/src/services/api.js:11`  
**Severity:** HIGH  
**Root Cause:** The API base URL is dynamically derived from the browser's current hostname. This breaks when the frontend is served from a different domain than the backend (e.g., Vercel frontend + Render backend).  
**Risk:** API calls fail in production.  
**Fix:** Use `import.meta.env.VITE_API_URL` with a proper fallback, and document it.

#### MEDIUM-1: No `users` router protection — admin endpoints exposed
**File:** `backend/routers/users.py`  
**Severity:** MEDIUM  
**Root Cause:** Even if the router was included, it has no auth. The `delete_user` endpoint does a hard deactivate (`is_active = False`), which is correct, but anyone can call it.  
**Risk:** Unauthorized admin actions.  
**Fix:** Add `get_current_user` + admin check.

#### MEDIUM-2: No pagination on list endpoints
**File:** All `GET` list endpoints  
**Severity:** MEDIUM  
**Root Cause:** All list endpoints return the entire table for a user. For a user with 10,000 expenses, this could be a 1MB+ JSON response.  
**Risk:** Performance degradation, memory exhaustion.  
**Fix:** Add `skip`/`limit` pagination to all list endpoints.

#### MEDIUM-3: `Notification` model missing `updated_at` and soft delete
**File:** `backend/models.py:169-180`  
**Severity:** MEDIUM  
**Root Cause:** The `Notification` model lacks `updated_at`, `is_deleted`, and `deleted_at` columns, unlike all other models. This inconsistency means notifications cannot be soft-deleted.  
**Risk:** Data inconsistency, accidental permanent deletion.  
**Fix:** Add `updated_at`, `is_deleted`, `deleted_at` to `Notification`.

#### MEDIUM-4: No `404` page in frontend routing
**File:** `frontend/src/App.jsx`  
**Severity:** MEDIUM  
**Root Cause:** `AppRoutes` has no catch-all route for unknown paths. A user visiting `/nonexistent` will see a blank page.  
**Risk:** Poor UX, broken links.  
**Fix:** Add `<Route path="*" element={<NotFound />} />`.

#### MEDIUM-5: `Frontend` has no `build` output optimization or code splitting
**File:** `frontend/vite.config.js`  
**Severity:** MEDIUM  
**Root Cause:** The Vite config is minimal with no build optimization, chunking, or source map configuration.  
**Risk:** Large bundle size, slow initial load.  
**Fix:** Add `build` configuration with chunking and minification.

#### LOW-1: `stripe` in `requirements.txt` is unused
**File:** `backend/requirements.txt:26`  
**Severity:** LOW  
**Root Cause:** `stripe==12.0.1` is listed but never imported anywhere.  
**Risk:** Bloat, unnecessary dependency.  
**Fix:** Remove `stripe`.

#### LOW-2: `Line` chart imported but unused in Dashboard
**File:** `frontend/src/pages/Dashboard.jsx:13`  
**Severity:** LOW  
**Root Cause:** `Line` is imported from `react-chartjs-2` but never used in the Dashboard component.  
**Risk:** Minor bundle bloat.  
**Fix:** Remove unused import.

#### LOW-3: `FALLBACK_RESPONSE` is static string, not dynamic
**File:** `backend/services/ai_service.py:39`  
**Severity:** LOW  
**Root Cause:** The fallback response is a hardcoded English string. In a multi-user platform, this could be jarring for non-English users.  
**Risk:** Minor UX issue.  
**Fix:** Consider i18n or at least a more neutral fallback.

---

### 1.2 DEPLOYMENT READINESS — CRITICAL GAPS

| File | Status | Issue |
|------|--------|-------|
| `Dockerfile` | MISSING | No containerization |
| `docker-compose.yml` | MISSING | No orchestration |
| `nginx.conf` | MISSING | No reverse proxy config |
| `.env.example` | MISSING | No environment template |
| `frontend/Dockerfile` | MISSING | No frontend containerization |
| `vite.config.js` | MINIMAL | No build optimization |
| `frontend/dist` | EXISTS | May be stale — should be gitignored |
| CORS config | BROKEN | `allow_origin_regex` too broad |
| API URL config | BROKEN | `window.location.hostname` fails in production |
| `.gitignore` | MISSING | No `.gitignore` at project root |

---

### 1.3 DATABASE — SCHEMA REVIEW

| Table | Status | Issues |
|-------|--------|--------|
| `users` | OK | `is_admin` added. Rebuild migration handles old schema. |
| `expenses` | OK | Soft delete, timestamps, FK. |
| `investments` | OK | Soft delete, timestamps, FK. |
| `loans` | OK | Soft delete, timestamps, FK. |
| `goals` | OK | Soft delete, timestamps, FK. |
| `budgets` | OK | Created by migration. |
| `notifications` | MISSING COLUMNS | No `updated_at`, `is_deleted`, `deleted_at` |

**Migration Script:** `migrate.py` is comprehensive and handles the `users` table rebuild correctly. However, it runs `PRAGMA foreign_keys=OFF` during rebuild which could cause orphaned records if the app is running concurrently.

---

### 1.4 API VALIDATION — ENDPOINT REVIEW

| Endpoint | Auth | Validation | Ownership | Pagination | Status |
|----------|------|------------|-----------|------------|--------|
| `POST /api/auth/register` | Public | ✅ | N/A | N/A | OK |
| `POST /api/auth/login` | Public | ✅ | N/A | N/A | OK |
| `POST /api/auth/refresh` | Public | ⚠️ (no body schema) | N/A | N/A | Needs body schema |
| `GET /api/auth/me` | Bearer | ✅ | ✅ | N/A | OK |
| `POST /api/auth/onboarding` | Bearer | ✅ | ✅ | N/A | OK |
| `POST /api/expenses` | Bearer | ✅ | ✅ | N/A | OK |
| `GET /api/expenses` | Bearer | ✅ | ✅ | ❌ | Needs pagination |
| `PUT /api/expenses/{id}` | Bearer | ✅ | ❌ | N/A | **MISSING ownership check** |
| `DELETE /api/expenses/{id}` | Bearer | ✅ | ❌ | N/A | **MISSING ownership check** |
| `GET /api/dashboard` | Bearer | ✅ | ✅ | N/A | OK |
| `POST /api/ai/ask-cfo` | Bearer | ✅ | ✅ | N/A | OK |
| `POST /api/ai/tools/execute` | Bearer | ✅ | ✅ | N/A | OK |

**CRITICAL FINDING:** `PUT /api/expenses/{id}` and `DELETE /api/expenses/{id}` do NOT verify that the expense belongs to `current_user.id`. An attacker could modify any expense by ID. Same issue may exist in `investments`, `loans`, `goals`, `budgets` routers.

---

### 1.5 AI SYSTEM REVIEW

| Component | Status | Notes |
|-----------|--------|-------|
| System Prompt | ✅ | Strong personality, tool instructions included |
| Tool Calling | ✅ | Two-pass execution implemented |
| Tool Registry | ✅ | 15 tools mapped |
| Error Handling | ⚠️ | `FALLBACK_RESPONSE` is static, no retry logic |
| Streaming | ⚠️ | Streaming does NOT support tools |
| Memory | ❌ | `ai_memory` column exists but is never read/written |
| Context | ✅ | Full financial context injected per request |
| Sanitization | ❌ | No prompt injection protection |

---

### 1.6 FRONTEND REVIEW

| Page | Status | Issues |
|------|--------|--------|
| Landing | ✅ | Responsive, animated, 3D hero |
| Login | ✅ | Form validation, password toggle |
| Register | ✅ | Currency selector, country input |
| Onboarding | ✅ | 3-step flow, goal selection |
| Dashboard | ✅ | KPIs, charts, insights, skeletons |
| Expenses | ✅ | Search, filter, charts, CRUD modal |
| Investments | ✅ | Allocation, ROI, search, CRUD modal |
| Loans | ✅ | Debt health, payoff, CRUD modal |
| Goals | ✅ | Progress rings, visualizer, CRUD modal |
| Budget | ✅ | Month selector, utilization bars |
| AI Chat | ✅ | Markdown, typing, persistence, tool actions |

**Missing:**
- 404 page
- Error boundaries
- Service worker
- PWA manifest
- SEO meta tags in `index.html`

---

### 1.7 SECURITY REVIEW

| Control | Status | Notes |
|---------|--------|-------|
| JWT Auth | ✅ | Access + refresh tokens, 7-day expiry |
| Password Hashing | ⚠️ | pbkdf2_sha256 (not bcrypt as documented) |
| Protected Routes | ✅ | FastAPI `Depends(get_current_user)` |
| User Isolation | ⚠️ | CRUD endpoints missing ownership check |
| Input Validation | ✅ | Pydantic v2 on all endpoints |
| XSS Protection | ❌ | No CSP headers, no output sanitization |
| SQL Injection | ✅ | SQLAlchemy ORM used (parameterized) |
| Rate Limiting | ❌ | No rate limiter installed |
| HTTPS | ❌ | No HTTPS redirect or HSTS |
| Admin Seed | ❌ | Password logged to console on every startup |
| CORS | ⚠️ | Regex too broad, credentials enabled |

---

### 1.8 PERFORMANCE REVIEW

| Area | Status | Notes |
|------|--------|-------|
| DB Queries | ⚠️ | No pagination, no query limits |
| API Calls | ⚠️ | Dashboard makes 4 parallel calls — could be 1 |
| React Rendering | ✅ | Functional components, no obvious memory leaks |
| Charts | ✅ | Responsive, theme-aware colors |
| AI Requests | ⚠️ | No caching, no debounce on chat input |
| Bundle Size | ⚠️ | No code splitting, no lazy loading |

---

## PHASE 9: DEPLOYMENT GAPS

### Missing Files (All Critical for Production)

1. `Dockerfile` (backend)
2. `Dockerfile` (frontend)
3. `docker-compose.yml`
4. `.env.example`
5. `nginx.conf` or `Caddyfile`
6. `.gitignore` (project root)
7. `frontend/.env.example`
8. `backend/gunicorn.conf.py` (for production server)

---

## RECOMMENDED FIX PRIORITY

### P0 (Deploy Blockers) — Fix Immediately
1. Add `app.include_router(users.router)` in `main.py`
2. Fix password hashing to use bcrypt (match `requirements.txt`)
3. Move `run_migrations()` and `seed_default_admin()` out of global scope
4. Remove `dotenv==0.9.9` from `requirements.txt`
5. Add ownership check to ALL PUT/DELETE endpoints in ALL routers
6. Fix CORS to use explicit origins from environment
7. Fix `api.js` to use a proper `VITE_API_URL` env variable
8. Create `Dockerfile` + `docker-compose.yml`
9. Add `.env.example` and `.gitignore`
10. Disable admin password logging

### P1 (Security) — Fix Before Public Launch
11. Add rate limiting to auth and AI endpoints
12. Add prompt injection sanitization
13. Protect `users.py` router with admin auth
14. Add CSP headers
15. Remove `stripe` from `requirements.txt`

### P2 (Performance/UX) — Fix Post-Launch
16. Add pagination to all list endpoints
17. Add `updated_at`/`is_deleted` to `Notification` model
18. Add 404 page to frontend
19. Add error boundaries
20. Optimize Vite build config

### P3 (Polish) — Nice to Have
21. Remove unused `Line` import from Dashboard
22. Add `get_or_create_user` removal/refactor
23. Add AI memory read/write functionality
24. Add streaming tool support

---

## PRODUCTION READINESS SCORE: 62/100

**Verdict:** The project is **functionally impressive** but has **critical deployment blockers** and **security gaps** that must be fixed before any real users access it. The modular architecture is solid, the UI is premium, and the AI tool calling works. With the P0 fixes applied, this can be deployed safely.
