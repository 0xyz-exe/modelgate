# Usage Accounting — ModelGate

**Version:** 1.0  
**Date:** 2026-10-17

## 1. Principles

**Accuracy:** Never inflate or deflate usage  
**Transparency:** Label data source (PROVIDER/ESTIMATED/UNKNOWN/DEMO)  
**Idempotency:** No double-counting  
**Auditability:** Every request tracked  

## 2. Usage Sources

### 2.1 PROVIDER (Highest Authority)

**Definition:** Token counts reported by upstream provider in response  
**Examples:** OpenAI `usage` field, Anthropic `usage` field  
**Label:** Green "PROVIDER" badge in UI  
**Trust:** Authoritative for billing  

**Extraction:**
```python
if response.get("usage"):
    input_tokens = response["usage"]["prompt_tokens"]
    output_tokens = response["usage"]["completion_tokens"]
    total_tokens = response["usage"]["total_tokens"]
    usage_source = "PROVIDER"
```

### 2.2 ESTIMATED (Calculated)

**Definition:** Token count estimated using known tokenizer  
**Examples:** tiktoken for OpenAI models, approximation for unknown models  
**Label:** Purple "ESTIMATED" badge in UI  
**Trust:** Guidance only, not for precise billing  

**Estimation:**
```python
import tiktoken
enc = tiktoken.encoding_for_model(model_name)
input_tokens = len(enc.encode(prompt))
output_tokens = len(enc.encode(response_text))
usage_source = "ESTIMATED"
```

**Accuracy:** ±5% for OpenAI models, ±20% for approximations

### 2.3 UNKNOWN (No Data)

**Definition:** Provider doesn't report usage and no reliable estimator available  
**Display:** "—" (em dash), NOT "0"  
**Label:** Gray "UNKNOWN" badge  
**Trust:** Cannot bill  

**Example:** Custom provider with no usage field, unsupported tokenizer

### 2.4 DEMO (Mock Data)

**Definition:** Deterministic fake usage from demo provider  
**Label:** Blue "DEMO" badge  
**Trust:** Not real usage, for testing only  

**Example:** Demo provider always returns 10 input / 20 output tokens

## 3. Token Counting Rules

### Rule 1: Never Assume Zero

**Wrong:** `tokens = response.get("usage", {}).get("prompt_tokens", 0)`  
**Right:** `tokens = response.get("usage", {}).get("prompt_tokens")  # None if missing`

**Database:** NULL for unknown, not 0

### Rule 2: Prefer Provider-Reported

**Priority:**
1. Provider response `usage` field
2. Estimation with known tokenizer
3. NULL (UNKNOWN)

### Rule 3: Label Everything

**Always store usage_source:**
```sql
INSERT INTO usage_records (input_tokens, output_tokens, usage_source)
VALUES (15, 8, 'PROVIDER');
```

### Rule 4: Don't Mix Sources in Aggregates

**Wrong:** Sum PROVIDER + ESTIMATED tokens  
**Right:** Separate charts/tables for each source

**Dashboard:** Filter by usage_source or show stacked bars with legend

## 4. Request Lifecycle Accounting

### 4.1 Successful Request

1. Client sends request to `/v1/chat/completions`
2. Gateway authenticates, validates, checks quota
3. Gateway routes to provider
4. Provider responds with 200 + usage metadata
5. Gateway records:
   - request (status=200, model_actual=...)
   - usage_record (tokens from provider, source=PROVIDER)
6. Gateway returns response to client

**Quota:** Deducted after step 5 (successful provider call)

### 4.2 Failed Request (Provider Error)

1-3. Same as successful
4. Provider responds with 500 error
5. Gateway records:
   - request (status=500, error_message=...)
   - usage_record (tokens=NULL if no usage in error, source=UNKNOWN)
6. Gateway returns error to client

**Quota:** Deducted if provider was called (consumed provider resources)

### 4.3 Failed Request (Gateway Validation)

1. Client sends invalid request
2. Gateway rejects (400) before provider call
3. Gateway records:
   - request (status=400, error_message="Invalid model")
   - NO usage_record (no provider call)

**Quota:** NOT deducted (rejected before spend)

### 4.4 Request with Retries

1. Client sends request
2. Gateway calls provider (attempt 1) → timeout
3. Gateway retries (attempt 2) → 500 error
4. Gateway retries (attempt 3) → 200 success
5. Gateway records:
   - request (status=200, retry_count=2, final usage)
   - usage_record (tokens from attempt 3, source=PROVIDER)
   - upstream_attempts (3 rows, one per attempt)

**Quota:** Deducted ONCE for successful attempt 3, not 3x

**Display:** Show "Retries: 2" in request detail, but usage counted once

## 5. Idempotency

### 5.1 Request ID as Idempotency Key

**Implementation:**
```sql
CREATE UNIQUE INDEX idx_usage_request_id ON usage_records(request_id);
```

**Insert:**
```python
try:
    db.execute(
        "INSERT INTO usage_records (id, request_id, ...) VALUES (?, ?, ...)",
        (usage_id, request_id, ...)
    )
except IntegrityError:
    # Already recorded, skip
    pass
```

### 5.2 Retry Safety

**Scenario:** Usage recording fails (DB timeout), gateway retries accounting

**Protection:** UNIQUE constraint prevents duplicate insert  
**Result:** Idempotent, usage recorded exactly once

## 6. Quota Deduction

### 6.1 Quota Types

**Request Quota:** Count of requests  
**Token Quota:** Sum of total_tokens (only when usage_source=PROVIDER)

### 6.2 Atomic Deduction

**PostgreSQL:**
```sql
UPDATE quota_policies
SET quota_used = quota_used + 1
WHERE id = ? AND quota_used + 1 <= quota_limit
RETURNING quota_used;
```

**Check:** If no rows returned, quota exceeded

**SQLite (MVP):**
```python
with db.begin():  # Transaction
    policy = db.query(QuotaPolicy).with_for_update().filter_by(id=policy_id).one()
    if policy.quota_used + tokens > policy.quota_limit:
        raise QuotaExceededError
    policy.quota_used += tokens
    db.commit()
```

### 6.3 Token Quota with UNKNOWN Usage

**Rule:** Don't deduct token quota when usage_source=UNKNOWN  
**Reason:** Cannot accurately track  
**Alternative:** Enforce request quota only

## 7. Cost Estimation

### 7.1 Pricing Configuration

**Storage:** pricing table (model_id, input_price_per_1k, output_price_per_1k, currency, effective_date)

**Example:**
```json
{
  "model_id": "gpt-3.5-turbo",
  "input_price_per_1k": 0.0015,
  "output_price_per_1k": 0.002,
  "currency": "USD",
  "effective_date": "2024-01-01"
}
```

### 7.2 Cost Calculation

**Formula:**
```python
if usage_source == "PROVIDER":
    cost = (input_tokens / 1000 * input_price) + (output_tokens / 1000 * output_price)
elif usage_source == "ESTIMATED":
    cost = estimated_calculation  # Label as ESTIMATED
else:
    cost = None  # Display as "—"
```

### 7.3 Cost Display

**UI:** Always show "Estimated: $X.XX" (never "Actual")  
**Reason:** Gateway doesn't receive provider invoices, only API-reported usage

**Export CSV:** `estimated_cost_usd` column

### 7.4 Free Tier Handling

**Rule:** Free tier usage still has cost=0.00, not cost=NULL  
**Reason:** Distinguish known-free from unknown pricing

## 8. Analytics Aggregation

### 8.1 Time-Series

**Query:**
```sql
SELECT 
  DATE(created_at) as date,
  usage_source,
  SUM(input_tokens) as total_input,
  SUM(output_tokens) as total_output
FROM usage_records
WHERE workspace_id = ?
GROUP BY DATE(created_at), usage_source
ORDER BY date DESC;
```

**Chart:** Stacked area, separate series per usage_source

### 8.2 Model Comparison

**Query:**
```sql
SELECT 
  model_id,
  usage_source,
  COUNT(*) as request_count,
  SUM(total_tokens) as total_tokens,
  AVG(latency_ms) as avg_latency
FROM usage_records
JOIN requests ON usage_records.request_id = requests.id
WHERE workspace_id = ?
GROUP BY model_id, usage_source;
```

### 8.3 Handling Mixed Sources

**Wrong:** Single bar showing PROVIDER + ESTIMATED sum  
**Right:** Side-by-side bars or stacked with legend

## 9. Export Format

**CSV Columns:**
```
request_id, timestamp, workspace, application, model_requested, model_actual, 
provider, status, latency_ms, input_tokens, output_tokens, total_tokens, 
usage_source, estimated_cost_usd, error_message
```

**Example:**
```csv
req_abc123,2024-10-17T14:30:00Z,demo,chatbot,gpt-3.5-turbo,gpt-3.5-turbo,openai,200,450,15,8,23,PROVIDER,0.000053,
req_def456,2024-10-17T14:31:00Z,demo,chatbot,gpt-4,gpt-4,openai,200,1200,20,15,35,ESTIMATED,0.000875,
req_ghi789,2024-10-17T14:32:00Z,demo,chatbot,custom-model,custom-model,custom,200,800,,,,,
```

## 10. Edge Cases

### 10.1 Streaming Responses

**Challenge:** Usage reported at end of stream  
**Solution:** Record usage after stream completes  
**Quota:** Check before stream starts, deduct after completion

### 10.2 Client Disconnect

**Challenge:** Stream interrupted mid-response  
**Solution:** Record partial usage if provider reports it, otherwise UNKNOWN

### 10.3 Provider Timeout

**Challenge:** Request times out, no response  
**Solution:** Record request (status=504), usage=NULL, source=UNKNOWN  
**Quota:** Deduct request count, not tokens (unknown)

### 10.4 Negative Tokens

**Challenge:** Provider returns negative usage (bug)  
**Validation:** Reject negative values, log error, set to NULL

### 10.5 Mismatched Total

**Challenge:** Provider reports total_tokens ≠ prompt + completion  
**Resolution:** Trust provider's total_tokens, log discrepancy

## 11. Testing Scenarios

**Test 1:** Provider reports usage → Verify source=PROVIDER  
**Test 2:** Provider omits usage → Verify source=UNKNOWN, tokens=NULL  
**Test 3:** Retry 3x → Verify single usage record  
**Test 4:** Duplicate insert → Verify no IntegrityError propagation  
**Test 5:** Concurrent quota deduction → Verify atomic behavior  
**Test 6:** CSV export → Verify all sources labeled  
**Test 7:** Dashboard chart → Verify separate series per source  

## 12. Monitoring

**Alerts:**
- Usage source=UNKNOWN exceeds 10% of requests (provider integration issue)
- Token quota exhausted (notify admin)
- Estimated vs actual cost diverges >20% (pricing config issue)

**Dashboards:**
- Usage source distribution pie chart
- Cost estimation accuracy (when actual bills available)
