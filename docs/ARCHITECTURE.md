# Architecture — ModelGate

**Version:** 1.0  
**Date:** 2026-10-17

## 1. System Overview

ModelGate is a modular monolith API gateway for AI inference requests.

**Architecture Style:** Layered monolith  
**Deployment:** Single process (MVP), horizontally scalable (future)  
**Database:** SQLite (local), PostgreSQL (production)  
**Rate Limiting:** In-memory (local), Redis (distributed)  

## 2. High-Level Architecture

```
┌─────────────┐
│   Client    │
│ Application │
└─────┬───────┘
      │ HTTPS + API Key
      ▼
┌─────────────────────────────────────┐
│         API Gateway (FastAPI)        │
│                                     │
│  ┌─────────────────────────────┐  │
│  │   Request Handler Layer     │  │
│  │  - Auth middleware          │  │
│  │  - Validation               │  │
│  │  - Rate limit check         │  │
│  │  - Quota check              │  │
│  └──────────┬──────────────────┘  │
│             │                      │
│  ┌──────────▼──────────────────┐  │
│  │   Business Logic Layer      │  │
│  │  - Model routing            │  │
│  │  - Provider selection       │  │
│  │  - Request normalization    │  │
│  └──────────┬──────────────────┘  │
│             │                      │
│  ┌──────────▼──────────────────┐  │
│  │   Provider Adapter Layer    │  │
│  │  - Demo provider            │  │
│  │  - OpenAI adapter           │  │
│  │  - Custom adapters          │  │
│  └──────────┬──────────────────┘  │
│             │                      │
│  ┌──────────▼──────────────────┐  │
│  │    Data Access Layer        │  │
│  │  - Usage recording          │  │
│  │  - Request logging          │  │
│  │  - Analytics queries        │  │
│  └─────────────────────────────┘  │
└─────────────┬───────────────────────┘
              │
        ┌─────▼──────┐
        │  Database  │
        │  (SQLite/  │
        │  Postgres) │
        └────────────┘

┌─────────────────────┐
│  Frontend (Next.js) │
│  - Dashboard        │
│  - API key mgmt     │
│  - Analytics        │
└──────────┬──────────┘
           │ REST API
           ▼
    (API Gateway)
```

## 3. Component Breakdown

### 3.1 API Gateway (Backend)

**Technology:** FastAPI + Python 3.11+ + Pydantic  
**Responsibilities:**
- HTTP request handling
- Authentication and authorization
- Request validation
- Rate limiting and quota enforcement
- Provider routing
- Response normalization
- Error handling
- Request/response logging

**Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings (env vars)
│   ├── dependencies.py      # Dependency injection
│   ├── middleware/
│   │   ├── auth.py          # API key auth
│   │   ├── rate_limit.py    # Rate limiting
│   │   └── error_handler.py # Error handling
│   ├── api/
│   │   ├── v1/
│   │   │   ├── chat.py      # /v1/chat/completions
│   │   │   ├── workspaces.py
│   │   │   ├── applications.py
│   │   │   ├── keys.py
│   │   │   ├── providers.py
│   │   │   ├── models.py
│   │   │   └── analytics.py
│   ├── models/              # Pydantic schemas
│   │   ├── request.py
│   │   ├── response.py
│   │   ├── workspace.py
│   │   └── usage.py
│   ├── db/
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── session.py       # DB session
│   │   └── migrations/      # Alembic
│   ├── services/
│   │   ├── gateway.py       # Core gateway logic
│   │   ├── routing.py       # Model routing
│   │   ├── usage.py         # Usage metering
│   │   ├── quota.py         # Quota enforcement
│   │   └── health.py        # Provider health
│   ├── providers/
│   │   ├── base.py          # Abstract interface
│   │   ├── demo.py          # Demo provider
│   │   ├── openai.py        # OpenAI adapter
│   │   └── registry.py      # Provider registry
│   └── utils/
│       ├── crypto.py        # Key hashing
│       ├── redaction.py     # PII redaction
│       └── tokens.py        # Token estimation
├── tests/
├── pyproject.toml
└── .env.example
```

### 3.2 Frontend (Dashboard)

**Technology:** Next.js 14 + React + TypeScript + Tailwind + shadcn/ui  
**Responsibilities:**
- User interface
- API key management
- Usage visualization
- Provider configuration
- Analytics dashboard
- Request inspection

**Structure:**
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx             # Dashboard
│   ├── workspaces/
│   ├── keys/
│   ├── providers/
│   ├── requests/
│   └── analytics/
├── components/
│   ├── ui/                  # shadcn components
│   ├── charts/
│   ├── tables/
│   └── forms/
├── lib/
│   ├── api.ts               # API client
│   ├── auth.ts              # Auth helpers
│   └── utils.ts
├── hooks/
│   ├── useWorkspaces.ts
│   ├── useProviders.ts
│   └── useAnalytics.ts
├── types/
│   └── api.ts
├── package.json
└── tsconfig.json
```

### 3.3 Database

**Technology:** SQLite (local), PostgreSQL (production)  
**ORM:** SQLAlchemy  
**Migrations:** Alembic  

**Entities:** (see DATABASE_DESIGN.md)
- workspaces
- applications
- api_keys
- providers
- models
- requests
- usage_records
- routing_policies
- quota_policies

### 3.4 Rate Limiting

**Local (MVP):** In-memory Python dict with sliding window  
**Distributed:** Redis with Lua scripts (future)  

**Algorithm:** Fixed window with atomic counters  
**Scopes:** Per key, per workspace  

## 4. Data Flow

### 4.1 Inference Request Flow

1. **Client** sends POST to `/v1/chat/completions` with API key
2. **Auth middleware** validates key, loads workspace/application
3. **Rate limit middleware** checks RPM limits, rejects if exceeded
4. **Quota middleware** checks quotas, rejects if exceeded
5. **Gateway service** validates request body (Pydantic)
6. **Routing service** selects provider and model
7. **Provider adapter** sends request to upstream provider
8. **Gateway service** normalizes response
9. **Usage service** records tokens and latency
10. **Response** returned to client

### 4.2 Usage Recording Flow

1. Request completes (success or failure)
2. Extract usage metadata (tokens, latency, status)
3. Create usage record with source label (PROVIDER/ESTIMATED/UNKNOWN)
4. Insert into database (idempotent on request_id)
5. Update quota counters
6. Log request details (redacted)

### 4.3 Provider Health Check Flow

1. Background task runs every 60s
2. For each configured provider:
   - Send lightweight health request
   - Record response time and status
   - Update provider status in database
   - Trigger circuit breaker if threshold exceeded
3. Dashboard polls provider status

## 5. Key Design Decisions

### 5.1 Modular Monolith

**Decision:** Single deployable unit, modular internal structure  
**Rationale:**
- Simpler deployment for MVP
- Lower operational complexity
- Easier to reason about
- Can extract services later if needed

**Trade-off:** Horizontal scaling requires state management (Redis for rate limits)

### 5.2 Provider Adapter Pattern

**Decision:** Abstract provider interface with concrete adapters  
**Rationale:**
- Isolates provider-specific code
- Easy to add new providers
- Testable with mocks
- Handles provider differences cleanly

**Interface:**
```python
class ProviderAdapter(ABC):
    @abstractmethod
    async def chat_completion(
        self, request: ChatRequest
    ) -> ChatResponse:
        pass
    
    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        pass
```

### 5.3 Request Normalization

**Decision:** Normalize provider responses to OpenAI-compatible format  
**Rationale:**
- Consistent client experience
- Easier usage tracking
- Simpler error handling

**Trade-off:** May not support all provider-specific features

### 5.4 Usage Source Labeling

**Decision:** Explicit labels (PROVIDER/ESTIMATED/UNKNOWN/DEMO)  
**Rationale:**
- Transparency about data quality
- Prevents false precision
- Enables trust in billing

**Implementation:** Enum field on usage records, displayed in all UIs

### 5.5 Atomic Quota Enforcement

**Decision:** Database-level constraints or Redis atomic operations  
**Rationale:**
- Prevents race conditions
- Ensures quota limits are hard
- Avoids double-charging

**Trade-off:** Requires database transaction or Redis

### 5.6 Idempotent Usage Recording

**Decision:** Request ID as idempotency key  
**Rationale:**
- Prevents double-counting on retries
- Safe retry of usage recording
- Consistent accounting

**Implementation:** UNIQUE constraint on request_id in usage_records

### 5.7 Server-Side Secrets

**Decision:** All provider credentials stored server-side only  
**Rationale:**
- Prevents credential leakage
- Frontend never sees provider keys
- Single point of control

**Trade-off:** Requires secure server secret management

## 6. Scalability Considerations

### 6.1 Current (MVP)

**Limits:**
- Single process
- SQLite (not concurrent writes)
- In-memory rate limits (not distributed)
- Max ~100 concurrent requests

**Suitable for:** Local development, small teams, demos

### 6.2 Future (Production)

**Improvements:**
- Multiple instances behind load balancer
- PostgreSQL for concurrent writes
- Redis for distributed rate limits
- Connection pooling
- Async workers for background tasks
- Caching layer (Redis)
- CDN for frontend

**Target:** 1000+ concurrent requests, multi-region

## 7. Security Architecture

### 7.1 Trust Boundaries

**Boundary 1:** Client → API Gateway
- Authentication: API key in Authorization header
- Validation: All inputs validated with Pydantic
- Rate limiting: Per key and workspace

**Boundary 2:** API Gateway → Provider
- Isolation: Provider credentials separate from client keys
- Validation: Provider URLs validated against allowlist
- Timeout: Hard timeouts prevent hanging requests

**Boundary 3:** API Gateway → Database
- Protection: Parameterized queries (SQLAlchemy ORM)
- Authorization: Workspace ID filtering on all queries

### 7.2 Secrets Management

**API Keys (Gateway):**
- Hash: SHA-256
- Storage: Database (only hash stored)
- Display: Full key shown once at creation

**Provider Credentials:**
- Storage: Environment variables (MVP)
- Future: HashiCorp Vault, AWS Secrets Manager

**JWT Tokens (Optional):**
- Algorithm: RS256
- Expiry: 1 hour
- Refresh: 7 days

### 7.3 Data Protection

**At Rest:**
- Database: File permissions (SQLite), encryption (PostgreSQL)
- Logs: Credentials redacted before writing

**In Transit:**
- HTTPS only (TLS 1.3)
- Certificate validation on provider requests

**In Memory:**
- Secrets cleared after use
- No logging of sensitive data

## 8. Observability

### 8.1 Logging

**Levels:** DEBUG, INFO, WARNING, ERROR  
**Format:** JSON structured logs  
**Fields:**
- timestamp
- level
- request_id
- workspace_id
- message
- metadata (redacted)

**Destinations:**
- stdout (MVP)
- File rotation (production)
- ELK stack (future)

### 8.2 Metrics

**Tracked:**
- Request rate (per endpoint)
- Response time (P50/P95/P99)
- Error rate (per status code)
- Provider availability
- Queue depth

**Export:** Prometheus format (future)

### 8.3 Tracing

**MVP:** Request ID propagation  
**Future:** OpenTelemetry with Jaeger

## 9. Testing Strategy

**Unit Tests:** pytest, 80%+ coverage on services  
**Integration Tests:** Test database, HTTP client with mocked providers  
**E2E Tests:** Playwright, critical user journeys  
**Load Tests:** Locust (future)  

## 10. Deployment

### 10.1 Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### 10.2 Production (Future)

**Container:** Docker multi-stage build  
**Orchestration:** Docker Compose (simple), Kubernetes (scale)  
**Database:** Managed PostgreSQL (RDS, Cloud SQL)  
**Cache:** Managed Redis (ElastiCache, Memorystore)  
**CDN:** Cloudflare, Fastly  

## 11. API Versioning

**Strategy:** URL path versioning (`/v1/`, `/v2/`)  
**Breaking Changes:** New major version  
**Deprecation:** 6-month notice, support two versions concurrently  

## 12. Error Handling

**Philosophy:** Fail fast, return clear errors, don't hide provider errors

**Error Response:**
```json
{
  "error": {
    "type": "rate_limit_error",
    "code": "rate_limit_exceeded", 
    "message": "Rate limit exceeded: 60 requests per minute",
    "request_id": "req_xxx"
  }
}
```

**Provider Errors:** Normalized to gateway error types, original error preserved in logs

## 13. Future Enhancements

**Streaming:** SSE for incremental responses  
**WebSockets:** Bi-directional communication  
**GraphQL:** Alternative to REST  
**Webhooks:** Event notifications  
**Multi-tenancy:** Isolated databases per tenant  
**Federation:** Multiple gateway instances  
