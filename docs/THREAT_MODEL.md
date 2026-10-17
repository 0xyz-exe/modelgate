# Threat Model — ModelGate

**Version:** 1.0  
**Date:** 2026-10-17

## 1. Assets

**High Value:**
- Provider API credentials
- Gateway API keys
- User request/response data (may contain PII/secrets)
- Usage and billing data

**Medium Value:**
- Workspace configuration
- Routing policies
- Provider health data

**Low Value:**
- Public documentation
- Model catalog metadata

## 2. Threat Actors

**External Attacker:** Internet-based, seeking data theft or service disruption  
**Malicious User:** Authenticated user attempting privilege escalation or data exfiltration  
**Compromised Provider:** Third-party AI provider may log or leak data  
**Insider Threat:** Out of scope for MVP (single user)  

## 3. Threats

### T1: API Key Theft

**Attack:** Attacker obtains valid gateway API key  
**Impact:** Unauthorized requests, quota exhaustion, cost inflation  
**Likelihood:** Medium  
**Mitigations:**
- Keys shown once at creation
- Secure hash storage (SHA-256)
- Key revocation
- Last-used timestamp monitoring
- Rate limits per key

### T2: Provider Credential Exposure

**Attack:** Attacker extracts provider credentials from database or logs  
**Impact:** Direct provider access, cost inflation, data exfiltration  
**Likelihood:** Medium  
**Mitigations:**
- Never store plaintext credentials
- Environment variables (MVP)
- Secrets manager (production)
- Credential redaction in logs
- No client-side exposure

### T3: Server-Side Request Forgery (SSRF)

**Attack:** Attacker configures provider base_url to internal service  
**Impact:** Internal network scanning, service access, data exfiltration  
**Likelihood:** High  
**Mitigations:**
- URL validation against allowlist
- Block private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8)
- Block cloud metadata endpoints (169.254.169.254)
- DNS rebinding protection
- Network-level egress rules

### T4: SQL Injection

**Attack:** Malicious input in API parameters  
**Impact:** Database read/write, data exfiltration  
**Likelihood:** Low  
**Mitigations:**
- SQLAlchemy ORM (no raw SQL)
- Parameterized queries
- Input validation (Pydantic)
- Principle of least privilege (DB user)

### T5: Cross-Workspace Data Leakage

**Attack:** User accesses another workspace's data  
**Impact:** Data breach, privacy violation  
**Likelihood:** Medium  
**Mitigations:**
- Workspace ID in all queries (WHERE workspace_id = ?)
- Authorization middleware
- Unit tests for isolation
- API key scoped to workspace

### T6: Rate Limit Bypass

**Attack:** Attacker bypasses rate limits via multiple keys or timing attacks  
**Impact:** Service degradation, quota exhaustion  
**Likelihood:** Medium  
**Mitigations:**
- Atomic counter updates
- Server-side enforcement
- Per-key AND per-workspace limits
- Distributed rate limiting (Redis, future)

### T7: Quota Race Condition

**Attack:** Concurrent requests exceed quota before counter updates  
**Impact:** Cost overrun, incorrect billing  
**Likelihood:** Medium  
**Mitigations:**
- Atomic database operations
- Pessimistic locking (SELECT FOR UPDATE)
- Idempotent usage recording

### T8: Request/Response Data Leakage

**Attack:** Sensitive user data in logs, error messages, or admin UI  
**Impact:** Privacy violation, compliance breach  
**Likelihood:** High  
**Mitigations:**
- Credential redaction in logs
- PII redaction (API keys, emails, tokens)
- Truncated request/response preview in UI
- "View full" requires auth check
- No sensitive data in error responses

### T9: Prompt Injection → SSRF/Exfiltration

**Attack:** Malicious prompt instructs model to reveal provider config or internal state  
**Impact:** Information disclosure  
**Likelihood:** Low (depends on provider model)  
**Mitigations:**
- Gateway doesn't execute model-generated code
- Provider credentials never in request context
- Limited (no shell access, no internal API calls)

### T10: Denial of Service (DoS)

**Attack:** Flood gateway with requests  
**Impact:** Service unavailable  
**Likelihood:** High  
**Mitigations:**
- Rate limits (hard caps)
- Payload size limits (10MB)
- Request timeout (65s)
- Connection limits
- Queue depth limits

### T11: Provider Impersonation

**Attack:** Attacker MitM connection to provider  
**Impact:** Data interception, modified responses  
**Likelihood:** Low  
**Mitigations:**
- HTTPS only
- Certificate validation
- No HTTPS downgrade

### T12: Duplicate Usage Accounting

**Attack:** Exploit retry logic to inflate usage charges  
**Impact:** Incorrect billing, cost inflation  
**Likelihood:** Medium  
**Mitigations:**
- Idempotent usage recording (request_id unique constraint)
- Retry count tracked
- Each upstream attempt logged separately, not summed

### T13: Authentication Bypass

**Attack:** Access gateway without valid API key  
**Impact:** Unauthorized usage  
**Likelihood:** Low  
**Mitigations:**
- Auth middleware on all protected routes
- No default/fallback auth
- API key required for /v1/* endpoints

### T14: Privilege Escalation

**Attack:** Limited user gains admin access  
**Impact:** Full system compromise  
**Likelihood:** Low (MVP: single user)  
**Mitigations:**
- Role-based permissions (future)
- Workspace isolation
- Admin endpoints separate

### T15: Dependency Vulnerabilities

**Attack:** Exploit known CVE in library  
**Impact:** Varies (RCE, DoS, data leak)  
**Likelihood:** Medium  
**Mitigations:**
- Dependency scanning (pip-audit, npm audit)
- Regular updates
- Minimal dependencies
- Pin versions

## 4. Attack Surface

**External:**
- `/v1/chat/completions` (public)
- `/api/workspaces` (authenticated)
- `/api/keys` (authenticated)
- `/api/providers` (authenticated admin)

**Internal:**
- Database (SQLite file, PostgreSQL socket)
- Provider HTTP endpoints

**Out of Scope:**
- Physical access
- Social engineering
- Supply chain attacks (MVP)

## 5. Security Controls

### Authentication

**API Key:** SHA-256 hash, Authorization header, per-request  
**Future:** JWT for dashboard users  

### Authorization

**Workspace isolation:** All queries filtered by workspace_id  
**API key scope:** Permissions array (read, write, admin)  
**Admin endpoints:** Separate auth check  

### Input Validation

**Pydantic schemas:** All request bodies  
**URL validation:** Regex + IP range check  
**Payload size:** 10MB limit  
**Field length:** Max 255 chars for names  

### Output Encoding

**JSON:** FastAPI automatic escaping  
**Logs:** Structured JSON, redacted fields  

### Cryptography

**Hashing:** SHA-256 for API keys  
**Secrets:** Fernet encryption (future)  
**TLS:** 1.3 minimum  

### Logging & Monitoring

**Access logs:** All API requests  
**Error logs:** Exceptions with redacted data  
**Audit log:** Key creation/revocation, provider config changes (future)  
**Anomaly detection:** Rate limit violations, unusual usage patterns (future)  

## 6. Compliance Considerations

**GDPR (Future):**
- Right to erasure (delete workspace)
- Data portability (CSV export)
- Consent for data processing
- Privacy policy

**SOC 2 (Future):**
- Audit logging
- Access controls
- Encryption at rest and in transit
- Incident response plan

**MVP:** No compliance certifications, document best practices

## 7. Incident Response (Future)

1. **Detection:** Monitoring alerts
2. **Containment:** Revoke compromised keys, block IPs
3. **Eradication:** Patch vulnerability
4. **Recovery:** Restore from backup
5. **Lessons Learned:** Update threat model

## 8. Residual Risks

**Accepted:**
- Single-user MVP (no RBAC)
- Local SQLite (no replication)
- Environment variable secrets (no Vault)
- No WAF (no DDoS protection)

**Future:**
- Multi-tenancy security
- Secrets rotation
- Advanced DDoS protection
- Penetration testing
