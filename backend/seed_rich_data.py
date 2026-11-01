import sqlite3
import uuid
import json
from datetime import datetime, timedelta

conn = sqlite3.connect('backend/modelgate.db')
cur = conn.cursor()

print("Seeding rich ModelGate telemetry, providers, models, and quotas...")

now = datetime.utcnow()
ws_id = "8c5acd89-4a6f-4448-bcb1-f8856eff9ee1" # Demo Workspace
app_id = "8ba7114a-7031-423a-8f43-e604348510f6" # Demo Application

# 1. Clean previous providers and models
cur.execute("DELETE FROM models")
cur.execute("DELETE FROM providers")
cur.execute("DELETE FROM quota_policies")

# 2. Providers
providers = [
    (str(uuid.uuid4()), ws_id, 'OpenAI Production Gateway', 'openai', 'https://api.openai.com/v1', json.dumps({"api_key": "sk-proj-...masked"}), json.dumps({"timeout_seconds": 30, "retries": 2}), 'healthy', now, now, now),
    (str(uuid.uuid4()), ws_id, 'Anthropic Claude Enterprise', 'anthropic', 'https://api.anthropic.com/v1', json.dumps({"api_key": "sk-ant-...masked"}), json.dumps({"timeout_seconds": 45, "retries": 1}), 'healthy', now, now, now),
    (str(uuid.uuid4()), ws_id, 'Mistral European Endpoints', 'mistral', 'https://api.mistral.ai/v1', json.dumps({"api_key": "mis-...masked"}), json.dumps({"timeout_seconds": 30, "retries": 2}), 'healthy', now, now, now),
    (str(uuid.uuid4()), ws_id, 'Local Deterministic Demo Provider', 'demo', 'http://127.0.0.1:8000/demo', json.dumps({}), json.dumps({"latency_simulation_ms": 45}), 'healthy', now, now, now)
]

for p in providers:
    cur.execute("""
    INSERT INTO providers (id, workspace_id, name, type, base_url, credentials, config, status, health_checked_at, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, p)

openai_id = providers[0][0]
anthropic_id = providers[1][0]
mistral_id = providers[2][0]
demo_id = providers[3][0]

# 3. Models
models_data = [
    (str(uuid.uuid4()), openai_id, 'gpt-4o', 'GPT-4o Omnimodal', json.dumps(["chat", "vision", "function_calling", "json_mode"]), 128000, 1, 'active', now, now),
    (str(uuid.uuid4()), openai_id, 'gpt-4o-mini', 'GPT-4o Mini Fast Inference', json.dumps(["chat", "function_calling"]), 128000, 1, 'active', now, now),
    (str(uuid.uuid4()), anthropic_id, 'claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet v2', json.dumps(["chat", "vision", "code", "artifacts"]), 200000, 1, 'active', now, now),
    (str(uuid.uuid4()), mistral_id, 'mistral-large-2407', 'Mistral Large Reasoning', json.dumps(["chat", "function_calling"]), 128000, 1, 'active', now, now),
    (str(uuid.uuid4()), demo_id, 'demo-gpt-3.5-turbo', 'ModelGate Deterministic Mock', json.dumps(["chat"]), 16384, 0, 'active', now, now),
]

for m in models_data:
    cur.execute("""
    INSERT INTO models (id, provider_id, model_id, display_name, capabilities, context_window, supports_streaming, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, m)

# 4. Quota Policy
cur.execute("""
INSERT INTO quota_policies (id, scope_type, scope_id, rate_limit_rpm, rate_limit_rph, rate_limit_rpd, quota_requests, quota_tokens, quota_used_requests, quota_used_tokens, quota_reset_policy, quota_reset_at, concurrent_limit, created_at, updated_at)
VALUES (?, 'application', ?, 600, 36000, 500000, 1000000, 50000000, 4820, 241900, 'monthly', ?, 25, ?, ?)
""", (str(uuid.uuid4()), app_id, (now + timedelta(days=30)).isoformat(), now, now))

# 5. Additional realistic API keys
cur.execute("""
INSERT INTO api_keys (id, application_id, key_hash, key_prefix, permissions, expires_at, revoked_at, last_used_at, created_at)
VALUES (?, ?, ?, 'mg_live_prod', ?, ?, NULL, ?, ?)
""", (str(uuid.uuid4()), app_id, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', json.dumps(["read", "write", "chat:completions"]), (now + timedelta(days=90)).isoformat(), now, now))

conn.commit()
conn.close()
print("ModelGate database seeding complete.")
