# Product Requirements Document — ModelGate

**Version:** 1.0  
**Date:** 2026-10-17  
**Status:** Draft

## 1. Product Vision

**Problem:** Developers building AI applications face:
- Multiple provider APIs with inconsistent interfaces
- Complex key management across providers
- No unified usage tracking
- Difficult quota enforcement
- Poor visibility into costs and failures
- No centralized rate limiting
- Hard-to-debug request failures

**Solution:** ModelGate provides a unified API gateway that:
- Normalizes provider interfaces
- Centralizes API key management
- Meters and tracks all usage
- Enforces quotas and rate limits
- Provides observability and debugging
- Routes requests with fallback policies
- Works locally without paid infrastructure

## 2. User Personas

**Primary: Backend Developer**
- Integrating AI into an application
- Needs reliable request handling
- Wants usage tracking per environment/customer
- Requires cost visibility
- Values debugging tools

**Secondary: DevOps/Platform Engineer**
- Managing AI infrastructure
- Enforcing organizational quotas
- Monitoring provider health
- Investigating incidents
- Setting rate limits

**Tertiary: Product Manager**
- Tracking feature usage
- Estimating costs
- Analyzing model performance
- Planning capacity

## 3. Functional Requirements

### 3.1 Core Gateway (P0)

**FR-001:** Unified inference API endpoint accepting chat completion requests  
**FR-002:** OpenAI-compatible request/response format where applicable  
**FR-003:** API key authentication on all gateway requests  
**FR-004:** Request validation (payload size, schema, parameters)  
**FR-005:** Model validation against catalog  
**FR-006:** Provider routing based on requested model  
**FR-007:** Normalized error responses  
**FR-008:** Request ID generation and tracking  
**FR-009:** Timeout enforcement (connect, read, total)  
**FR-010:** Response normalization across providers  

### 3.2 Provider Adapters (P0)

**FR-011:** Abstract provider interface  
**FR-012:** Demo/mock provider (no external calls)  
**FR-013:** OpenAI-compatible provider adapter  
**FR-014:** Configurable provider base URLs  
**FR-015:** Provider credential management (server-side only)  
**FR-016:** Provider-specific error handling  
**FR-017:** Usage metadata extraction  
**FR-018:** Provider timeout configuration  
**FR-019:** Provider health status tracking  

### 3.3 Authentication & Authorization (P0)

**FR-020:** Workspace creation  
**FR-021:** Application registration within workspace  
**FR-022:** Gateway API key generation (cryptographically secure)  
**FR-023:** API key scoping (workspace, application, permissions)  
**FR-024:** Secure key storage (hashed)  
**FR-025:** Key display once at creation  
**FR-026:** Key revocation  
**FR-027:** Last-used timestamp tracking  
**FR-028:** Workspace isolation enforcement  
**FR-029:** Cross-workspace access prevention  

### 3.4 Usage Metering (P0)

**FR-030:** Request record persistence (all attempts)  
**FR-031:** Provider-reported token usage capture  
**FR-032:** Input/output/total token tracking  
**FR-033:** Usage source labeling (PROVIDER/ESTIMATED/UNKNOWN)  
**FR-034:** Request latency recording  
**FR-035:** Success/error status tracking  
**FR-036:** Actual model used (not just requested)  
**FR-037:** Retry count tracking  
**FR-038:** Idempotent usage accounting  
**FR-039:** No double-counting on retries  
**FR-040:** Aggregation by time/workspace/app/model/provider  

### 3.5 Rate Limiting & Quotas (P0)

**FR-041:** Per-key request rate limits (RPM)  
**FR-042:** Per-workspace request rate limits (RPM)  
**FR-043:** Daily request quotas  
**FR-044:** Token quotas (where measurable)  
**FR-045:** Concurrent request limits  
**FR-046:** Server-side enforcement  
**FR-047:** Atomic limit checking  
**FR-048:** Rate limit response headers  
**FR-049:** Quota reset tracking  
**FR-050:** Rejected request logging (not counted as usage)  

### 3.6 Model Catalog & Routing (P0)

**FR-051:** Model catalog (provider, ID, capabilities)  
**FR-052:** Streaming support indicators  
**FR-053:** Model availability status  
**FR-054:** Explicit model selection  
**FR-055:** Model authorization per workspace  
**FR-056:** Requested vs actual model tracking  
**FR-057:** Unknown model rejection  

### 3.7 Request Logging & Debugging (P1)

**FR-058:** Request detail persistence  
**FR-059:** Request/response body storage (redacted)  
**FR-060:** Error message capture  
**FR-061:** Request timeline (start/end/duration)  
**FR-062:** Upstream attempt details  
**FR-063:** Credential redaction in logs  
**FR-064:** Log search and filtering  
**FR-065:** Workspace-scoped log access  

### 3.8 Reliability (P1)

**FR-066:** Configurable retry policies  
**FR-067:** Exponential backoff with jitter  
**FR-068:** Non-retry of validation errors  
**FR-069:** Provider health checks  
**FR-070:** Circuit breaker behavior  
**FR-071:** Fallback model configuration  
**FR-072:** Fallback policy enforcement  
**FR-073:** Request cancellation support  

### 3.9 Dashboard & Analytics (P1)

**FR-074:** Request volume charts  
**FR-075:** Success/error rate metrics  
**FR-076:** Latency percentiles (P50/P95/P99)  
**FR-077:** Usage by model  
**FR-078:** Usage by workspace/application  
**FR-079:** Provider health dashboard  
**FR-080:** Quota utilization display  
**FR-081:** CSV/JSON export  
**FR-082:** Time range filtering  
**FR-083:** Empty state handling  

### 3.10 Cost Estimation (P2)

**FR-084:** Optional pricing configuration  
**FR-085:** Cost estimation per request  
**FR-086:** Separate estimated from actual billing  
**FR-087:** Unknown pricing display  
**FR-088:** Pricing source and date tracking  

### 3.11 Streaming (P2)

**FR-089:** Server-sent events (SSE) streaming responses  
**FR-090:** Partial failure handling  
**FR-091:** Usage accounting for streamed requests  
**FR-092:** Client disconnect handling  

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-001:** Gateway latency overhead <50ms (P50)  
**NFR-002:** Support 100 concurrent requests (local MVP)  
**NFR-003:** Database query response time <100ms (P95)  
**NFR-004:** Dashboard load time <2s  

### 4.2 Security

**NFR-005:** No plaintext storage of gateway keys  
**NFR-006:** No client-side exposure of provider credentials  
**NFR-007:** SSRF prevention on configurable URLs  
**NFR-008:** Input validation on all endpoints  
**NFR-009:** Credential redaction in all logs  
**NFR-010:** SQL injection prevention  
**NFR-011:** Rate limit bypass prevention  
**NFR-012:** Workspace isolation enforcement  

### 4.3 Reliability

**NFR-013:** 99.9% uptime for gateway (excluding provider outages)  
**NFR-014:** Zero usage double-counting  
**NFR-015:** Atomic quota enforcement  
**NFR-016:** Graceful provider failure handling  

### 4.4 Usability

**NFR-017:** Local installation in <10 minutes  
**NFR-018:** API documentation with examples  
**NFR-019:** Clear error messages  
**NFR-020:** Accessible UI (WCAG 2.1 AA)  
**NFR-021:** Responsive layout (mobile/tablet/desktop)  

### 4.5 Maintainability

**NFR-022:** Type-safe codebase (Python type hints, TypeScript)  
**NFR-023:** Automated tests (>80% coverage for critical paths)  
**NFR-024:** Database migrations  
**NFR-025:** Modular architecture  

## 5. Primary User Journey

**Goal:** Send an AI request through the gateway and inspect usage.

1. **Setup:** User installs ModelGate locally
2. **Workspace:** Create a workspace "Production"
3. **Application:** Register application "ChatBot v1"
4. **Provider:** Configure demo provider (or optional real provider)
5. **API Key:** Generate scoped API key for ChatBot v1
6. **Request:** Send POST to `/v1/chat/completions` with API key
7. **Response:** Receive normalized response with request ID
8. **Inspect:** View request in dashboard
9. **Usage:** See token counts (labeled as DEMO/PROVIDER/ESTIMATED)
10. **Quota:** Set 100 request daily limit
11. **Enforce:** Make 101st request, receive 429 error
12. **Debug:** Inspect error details in logs
13. **Export:** Download usage CSV

## 6. Acceptance Criteria

**Milestone A — Discovery:**
- [ ] Repository audit complete
- [ ] PRD reviewed
- [ ] UI/UX brief created
- [ ] Architecture documented
- [ ] Threat model documented

**Milestone B — Gateway Foundation:**
- [ ] Demo provider responds to requests
- [ ] API key authentication works
- [ ] Request validation rejects invalid payloads
- [ ] Responses normalized
- [ ] Request IDs generated
- [ ] Basic request logging

**Milestone C — Usage & Controls:**
- [ ] Usage records persist
- [ ] Token counts labeled correctly (PROVIDER/ESTIMATED/UNKNOWN)
- [ ] Rate limits enforced
- [ ] Quotas enforced
- [ ] Key revocation blocks requests
- [ ] Workspace isolation tested

**Milestone D — Routing & Reliability:**
- [ ] Model catalog queried
- [ ] Routing selects correct provider
- [ ] Timeouts enforced
- [ ] Retries bounded
- [ ] Provider health tracked
- [ ] Fallback policy configurable

**Milestone E — Dashboard:**
- [ ] Usage analytics display
- [ ] Request search works
- [ ] Request detail view shows redacted data
- [ ] Provider health visible
- [ ] API docs accessible

**Milestone F — Hardening:**
- [ ] Security audit completed
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E Playwright tests pass
- [ ] Documentation complete
- [ ] Git history clean

## 7. Provider & Model Capabilities

### 7.1 Supported Providers (MVP)

**Demo Provider (P0):**
- Deterministic responses
- Configurable latency/errors
- No external calls
- Labeled as DEMO in all UI/logs

**OpenAI-Compatible (P1):**
- Any OpenAI API-compatible endpoint
- Includes OpenRouter, local Ollama, etc.
- Configurable base URL
- Validated against allowlist

### 7.2 Model Capabilities

**Basic (P0):**
- Text/chat completion
- System and user messages
- Temperature/top_p parameters
- Max tokens

**Advanced (P2):**
- Streaming
- Function calling
- Vision
- JSON mode

**MVP focuses on basic capabilities only.**

## 8. Rate Limit & Quota Semantics

### 8.1 Rate Limits (Requests Per Minute)

**Algorithm:** Fixed window  
**Scope:** Per key, per workspace  
**Reset:** Top of each minute  
**Behavior:** Reject with 429 when exceeded  
**Headers:** X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset  

### 8.2 Quotas (Daily/Total Requests or Tokens)

**Algorithm:** Counter with reset  
**Scope:** Per key, per workspace  
**Reset:** Configurable (daily at midnight, never, manual)  
**Behavior:** Hard reject with 429  
**UI:** Show utilization percentage  

### 8.3 Concurrent Request Limits

**Scope:** Per workspace  
**Behavior:** Queue or reject based on policy  

## 9. Usage Accounting Rules

### 9.1 Token Counting

**Priority:**
1. Provider-reported usage (label: PROVIDER)
2. Estimation from known tokenizer (label: ESTIMATED)
3. Unknown (label: UNKNOWN, display as "—" not 0)

**Never assume zero usage when provider doesn't report.**

### 9.2 Retry Accounting

**Rule:** Each upstream attempt recorded separately.  
**Quota:** Deduct only on successful provider call.  
**Display:** Show retry count, don't multiply usage.  

### 9.3 Failed Requests

**Rule:** Record request and error.  
**Quota:** Don't deduct if validation fails before provider call.  
**Quota:** Deduct if provider call made but provider returns error (consumed provider quota).  

### 9.4 Idempotency

**Rule:** Request ID must be idempotent key for usage.  
**Implementation:** Database constraint or check before insert.  

## 10. Reliability & Performance Requirements

### 10.1 Timeouts

**Connect:** 5 seconds  
**Read:** 60 seconds  
**Total:** 65 seconds  

### 10.2 Retries

**Eligible:** 5xx errors, timeouts, connection failures  
**Not eligible:** 4xx errors (except 429)  
**Max attempts:** 3  
**Backoff:** Exponential with jitter (1s, 2s, 4s)  

### 10.3 Health Checks

**Frequency:** Every 60 seconds  
**Failure threshold:** 3 consecutive failures  
**Recovery threshold:** 1 success  
**Behavior:** Mark unavailable, skip in routing  

## 11. Security & Privacy Requirements

### 11.1 Secrets Management

**Gateway API Keys:** SHA-256 hashed, display once  
**Provider Credentials:** Environment variables or secrets manager  
**User Passwords:** bcrypt (if user auth added)  

### 11.2 Data Redaction

**Logs:** Redact Authorization headers  
**Logs:** Redact API keys in query params  
**UI:** Never display full provider credentials  
**Export:** Optionally redact prompt content  

### 11.3 Access Control

**Rule:** Workspace members see only their workspace data.  
**Enforcement:** Database-level workspace_id filter on all queries.  
**Admin:** Optional super-admin role (out of scope for MVP).  

## 12. Local Installation & Demo Requirements

### 12.1 Installation

**Time:** <10 minutes  
**Dependencies:** Python 3.11+, Node 18+, Docker optional  
**Database:** SQLite default  
**Commands:**
```bash
git clone <repo>
cd modelgate
./scripts/setup.sh  # or equivalent
```

### 12.2 Demo Mode

**Feature:** Works without external provider credentials  
**Provider:** Built-in demo provider  
**Data:** Deterministic responses  
**Label:** All demo requests clearly marked  

## 13. Known Limitations (MVP)

- No streaming support
- No function calling
- No vision models
- Single user (no multi-tenancy)
- No billing/payments
- No email notifications
- No SSO
- No audit log export
- Local rate limiting (not distributed)
- SQLite (not production-scale)
- No automatic model catalog updates
- Manual provider configuration
- No GraphQL API
- No webhooks

## 14. Out of Scope (Explicitly Excluded)

- Payment processing
- Billing subscriptions
- Multi-region deployment
- CDN integration
- Model fine-tuning
- Dataset management
- Prompt engineering tools
- Collaboration features
- Third-party integrations beyond providers
- Mobile apps
- Browser extensions

## 15. Success Metrics

**Adoption:**
- Local installations
- GitHub stars
- Community contributions

**Technical:**
- Gateway latency P95 <100ms
- Zero usage double-counting incidents
- Test coverage >80% for critical paths

**User satisfaction:**
- Setup time <10 minutes
- Issue resolution time <48 hours
- Documentation completeness (measured by FAQ hits)

## 16. Risks & Mitigations

**Risk:** Provider rate limits exhaust quota quickly  
**Mitigation:** Implement circuit breakers, expose provider limits in UI

**Risk:** Token estimation inaccurate  
**Mitigation:** Clearly label estimates, allow manual correction

**Risk:** Concurrent requests cause quota races  
**Mitigation:** Use atomic database operations or Redis

**Risk:** Large prompts exceed memory  
**Mitigation:** Implement payload size limits

**Risk:** Provider API changes break adapters  
**Mitigation:** Version adapter interfaces, integration tests

## 17. Future Enhancements (Post-MVP)

**P1:**
- Streaming support
- Redis-based distributed rate limiting
- PostgreSQL support
- Workspace teams and RBAC
- Webhook notifications
- Cost budgets and alerts

**P2:**
- Function calling support
- Vision model support
- Auto-scaling based on load
- Multi-region deployment
- SSO integration
- Advanced analytics (cost trends, model comparison)

**P3:**
- Prompt caching
- Request deduplication
- A/B testing framework
- Custom model routing algorithms
- Marketplace for custom adapters
