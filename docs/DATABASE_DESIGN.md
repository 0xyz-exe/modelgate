# Database Design — ModelGate

**Version:** 1.0  
**Date:** 2026-10-17

## 1. Schema Overview

**Database:** SQLite (local), PostgreSQL (production)  
**ORM:** SQLAlchemy 2.0  
**Migrations:** Alembic  

## 2. Entity Relationship Diagram

```
workspaces
    ├─→ applications
    │       ├─→ api_keys
    │       └─→ requests
    ├─→ providers (config)
    ├─→ routing_policies
    └─→ quota_policies

models (catalog)
    ├─→ requests
    └─→ usage_records

requests
    └─→ usage_records
```

## 3. Tables

### 3.1 workspaces

**Purpose:** Isolation boundary for multi-tenant use

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Workspace ID |
| name | VARCHAR(255) | NOT NULL | Display name |
| slug | VARCHAR(255) | UNIQUE, NOT NULL | URL-safe identifier |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (slug)

### 3.2 applications

**Purpose:** Logical grouping within workspace (e.g., "production", "staging")

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Application ID |
| workspace_id | UUID | FK, NOT NULL | Parent workspace |
| name | VARCHAR(255) | NOT NULL | Display name |
| description | TEXT | NULL | Optional description |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- PRIMARY KEY (id)
- INDEX (workspace_id)
- UNIQUE (workspace_id, name)

### 3.3 api_keys

**Purpose:** Gateway authentication credentials

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Key ID |
| application_id | UUID | FK, NOT NULL | Parent application |
| key_hash | VARCHAR(64) | UNIQUE, NOT NULL | SHA-256 hash of key |
| key_prefix | VARCHAR(16) | NOT NULL | First 8 chars (for display) |
| permissions | TEXT | NOT NULL | JSON array of permissions |
| expires_at | TIMESTAMP | NULL | Optional expiration |
| revoked_at | TIMESTAMP | NULL | Revocation timestamp |
| last_used_at | TIMESTAMP | NULL | Last successful auth |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (key_hash)
- INDEX (application_id)
- INDEX (revoked_at) WHERE revoked_at IS NULL

**Notes:**
- Actual key never stored, only SHA-256 hash
- key_prefix allows display in UI without exposing full key

### 3.4 providers

**Purpose:** Provider configuration (credentials, URLs, settings)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Provider ID |
| workspace_id | UUID | FK, NOT NULL | Workspace scope |
| name | VARCHAR(255) | NOT NULL | Provider name |
| type | VARCHAR(50) | NOT NULL | demo, openai, custom |
| base_url | TEXT | NULL | API base URL |
| credentials | TEXT | NULL | Encrypted JSON |
| config | TEXT | NOT NULL | JSON config (timeouts, etc.) |
| status | VARCHAR(20) | NOT NULL | active, degraded, down |
| health_checked_at | TIMESTAMP | NULL | Last health check |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- PRIMARY KEY (id)
- INDEX (workspace_id)
- INDEX (status)

**Notes:**
- credentials encrypted at rest (future)
- Demo provider: type='demo', no credentials required

### 3.5 models

**Purpose:** Model catalog (capabilities, availability)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Model ID |
| provider_id | UUID | FK, NOT NULL | Provider |
| model_id | VARCHAR(255) | NOT NULL | Provider's model identifier |
| display_name | VARCHAR(255) | NOT NULL | Human-readable name |
| capabilities | TEXT | NOT NULL | JSON array (chat, streaming, etc.) |
| context_window | INTEGER | NULL | Max context tokens (if known) |
| supports_streaming | BOOLEAN | NOT NULL | Streaming support |
| status | VARCHAR(20) | NOT NULL | available, unavailable |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- PRIMARY KEY (id)
- INDEX (provider_id)
- UNIQUE (provider_id, model_id)
- INDEX (status)

### 3.6 routing_policies

**Purpose:** Model routing rules per workspace

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Policy ID |
| workspace_id | UUID | FK, UNIQUE, NOT NULL | Workspace |
| default_model_id | UUID | FK, NULL | Default model |
| allowed_providers | TEXT | NOT NULL | JSON array of provider IDs |
| allowed_models | TEXT | NOT NULL | JSON array of model IDs |
| fallback_enabled | BOOLEAN | NOT NULL | Enable fallback |
| fallback_model_id | UUID | FK, NULL | Fallback model |
| fallback_conditions | TEXT | NOT NULL | JSON config |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (workspace_id)

### 3.7 quota_policies

**Purpose:** Rate limits and quotas per API key or workspace

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Policy ID |
| scope_type | VARCHAR(20) | NOT NULL | api_key, workspace |
| scope_id | UUID | NOT NULL | API key or workspace ID |
| rate_limit_rpm | INTEGER | NULL | Requests per minute |
| rate_limit_rph | INTEGER | NULL | Requests per hour |
| rate_limit_rpd | INTEGER | NULL | Requests per day |
| quota_requests | INTEGER | NULL | Total request quota |
| quota_tokens | INTEGER | NULL | Total token quota |
| quota_reset_policy | VARCHAR(20) | NOT NULL | never, daily, weekly, monthly |
| quota_reset_at | TIMESTAMP | NULL | Next reset time |
| concurrent_limit | INTEGER | NULL | Max concurrent requests |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- PRIMARY KEY (id)
- INDEX (scope_type, scope_id)
- UNIQUE (scope_type, scope_id)

### 3.8 requests

**Purpose:** Request log with full lifecycle

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Request ID (client-visible) |
| workspace_id | UUID | FK, NOT NULL | Workspace |
| application_id | UUID | FK, NOT NULL | Application |
| api_key_id | UUID | FK, NOT NULL | API key used |
| model_requested | VARCHAR(255) | NOT NULL | Model client requested |
| model_actual | VARCHAR(255) | NULL | Model actually used |
| provider_id | UUID | FK, NULL | Provider used |
| status_code | INTEGER | NOT NULL | HTTP status |
| started_at | TIMESTAMP | NOT NULL | Request start |
| completed_at | TIMESTAMP | NULL | Request completion |
| latency_ms | INTEGER | NULL | Total latency |
| retry_count | INTEGER | NOT NULL | Number of retries |
| error_type | VARCHAR(50) | NULL | Error classification |
| error_message | TEXT | NULL | Error details |
| request_body | TEXT | NULL | Redacted request JSON |
| response_body | TEXT | NULL | Redacted response JSON |
| created_at | TIMESTAMP | NOT NULL | Log timestamp |

**Indexes:**
- PRIMARY KEY (id)
- INDEX (workspace_id, created_at DESC)
- INDEX (application_id, created_at DESC)
- INDEX (api_key_id, created_at DESC)
- INDEX (status_code)
- INDEX (provider_id)
- INDEX (started_at DESC)

**Notes:**
- id is the request_id returned to client
- request_body and response_body redacted for PII

### 3.9 usage_records

**Purpose:** Token usage and metering

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Usage record ID |
| request_id | UUID | FK, UNIQUE, NOT NULL | Parent request |
| workspace_id | UUID | FK, NOT NULL | Workspace (denormalized) |
| application_id | UUID | FK, NOT NULL | Application (denormalized) |
| model_id | UUID | FK, NULL | Model used |
| provider_id | UUID | FK, NULL | Provider used |
| input_tokens | INTEGER | NULL | Input token count |
| output_tokens | INTEGER | NULL | Output token count |
| total_tokens | INTEGER | NULL | Total tokens |
| usage_source | VARCHAR(20) | NOT NULL | PROVIDER, ESTIMATED, UNKNOWN, DEMO |
| estimated_cost | DECIMAL(10,6) | NULL | Estimated cost USD |
| created_at | TIMESTAMP | NOT NULL | Usage timestamp |

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (request_id)
- INDEX (workspace_id, created_at DESC)
- INDEX (application_id, created_at DESC)
- INDEX (model_id)
- INDEX (provider_id)
- INDEX (usage_source)
- INDEX (created_at DESC)

**Notes:**
- request_id UNIQUE constraint ensures idempotent usage recording
- usage_source enum: PROVIDER (from API), ESTIMATED (tokenizer), UNKNOWN (no data), DEMO (mock)
- Tokens NULL when truly unknown; don't default to 0

### 3.10 provider_health

**Purpose:** Provider health check history

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Health check ID |
| provider_id | UUID | FK, NOT NULL | Provider |
| status | VARCHAR(20) | NOT NULL | healthy, degraded, down |
| latency_ms | INTEGER | NULL | Health check latency |
| error_message | TEXT | NULL | Error if failed |
| checked_at | TIMESTAMP | NOT NULL | Check timestamp |

**Indexes:**
- PRIMARY KEY (id)
- INDEX (provider_id, checked_at DESC)

**Notes:**
- Retention: 7 days for analytics

### 3.11 audit_log

**Purpose:** Security-sensitive actions (future)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Log entry ID |
| workspace_id | UUID | FK, NULL | Workspace |
| actor_id | UUID | NULL | User ID |
| action | VARCHAR(100) | NOT NULL | Action type |
| resource_type | VARCHAR(50) | NOT NULL | Resource affected |
| resource_id | UUID | NULL | Resource ID |
| metadata | TEXT | NULL | JSON details |
| created_at | TIMESTAMP | NOT NULL | Action timestamp |

**Indexes:**
- PRIMARY KEY (id)
- INDEX (workspace_id, created_at DESC)
- INDEX (actor_id, created_at DESC)
- INDEX (action)

## 4. Data Types

**UUID:** Primary keys (v4)  
**TIMESTAMP:** ISO 8601, UTC, with timezone  
**TEXT:** JSON stored as TEXT, validated in application  
**DECIMAL:** For currency (10,6 = up to 9999.999999)  

## 5. Constraints and Rules

### 5.1 Cascading Deletes

- workspace deleted → cascade to applications, providers, routing_policies
- application deleted → cascade to api_keys, requests
- api_key deleted → set NULL on requests.api_key_id (preserve history)
- provider deleted → set NULL on requests.provider_id (preserve history)

### 5.2 Soft Deletes

- api_keys: revoked_at instead of DELETE

### 5.3 Validation Rules

**Workspace slug:** `^[a-z0-9-]+$`, max 255 chars  
**API key prefix:** `mg_[a-zA-Z0-9]{8}...`  
**Status enums:** Validated in application layer (Pydantic)  

## 6. Migrations

**Tool:** Alembic  
**Location:** `backend/alembic/versions/`  
**Naming:** `YYYY_MM_DD_HHMM_description.py`  

**Initial migration:**
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

## 7. Seed Data

**Demo workspace:**
- slug: "demo"
- Application: "Demo App"
- API key: generated on first run
- Provider: Demo provider (pre-configured)

## 8. Indexes Strategy

**Query patterns:**
- List requests by workspace + time range → INDEX (workspace_id, created_at DESC)
- List usage by application → INDEX (application_id, created_at DESC)
- Authenticate API key → UNIQUE (key_hash)
- Provider health dashboard → INDEX (provider_id, checked_at DESC)

**Avoid over-indexing:** Only add indexes for proven slow queries

## 9. Data Retention

**MVP:** No automatic deletion  
**Future:**
- requests: 90 days
- usage_records: 1 year
- provider_health: 7 days
- audit_log: 2 years

**Implementation:** Background job (cron) with configurable retention

## 10. Database Sizing

**MVP (SQLite):**
- ~1M requests → ~500MB
- ~1M usage records → ~300MB
- Total: <1GB for typical local use

**Production (PostgreSQL):**
- Partitioning by created_at (monthly)
- Archive old partitions to S3
- Target: <100GB active data

## 11. Backup Strategy

**SQLite:** File copy + timestamp  
**PostgreSQL:** pg_dump daily + WAL archiving  

## 12. Performance Considerations

**Connection pooling:** 10-20 connections (production)  
**Query timeout:** 10 seconds  
**Batch inserts:** Usage records batched where possible  
**Read replicas:** Future for analytics queries  

## 13. Security

**SQL injection:** Prevented by SQLAlchemy ORM  
**Row-level security:** Workspace ID filtering on all queries  
**Secrets:** Never store plaintext provider credentials (encrypt with Fernet)  
