"""Unit tests for quota enforcement"""
import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Workspace, Application, QuotaPolicy, UsageRecord, Request, APIKey
from app.services.quota import quota_enforcer


@pytest.fixture
def test_workspace(db: Session = SessionLocal()):
    """Create test workspace"""
    ws = Workspace(name="Quota Test", slug="quota-test")
    db.add(ws)
    db.commit()
    db.refresh(ws)
    yield ws
    db.delete(ws)
    db.commit()


def test_no_quota_policy():
    """Test unlimited when no policy exists"""
    db = SessionLocal()
    
    # Random workspace ID (no policy)
    allowed, info = quota_enforcer.check_quota(
        db=db,
        workspace_id="nonexistent"
    )
    
    assert allowed
    assert info["quota_enabled"] == False
    db.close()


def test_quota_within_limit():
    """Test quota allows requests within limit"""
    db = SessionLocal()
    
    # Create workspace
    import uuid
    ws = Workspace(name="Test WS", slug=f"test-quota-1-{uuid.uuid4().hex[:6]}")
    db.add(ws)
    db.commit()
    
    # Create quota policy: 1000 tokens daily
    policy = QuotaPolicy(
        scope_type="workspace",
        scope_id=ws.id,
        quota_tokens=1000,
        quota_used_tokens=0,
        quota_reset_policy="daily"
    )
    db.add(policy)
    db.commit()
    
    # Check quota (no usage yet)
    allowed, info = quota_enforcer.check_quota(
        db=db,
        workspace_id=ws.id
    )
    
    assert allowed
    assert info["quota_enabled"] == True
    assert info["limit"] == 1000
    assert info["used"] == 0
    assert info["remaining"] == 1000
    
    # Cleanup
    db.delete(policy)
    db.delete(ws)
    db.commit()
    db.close()


def test_quota_exceeded():
    """Test quota blocks when limit exceeded"""
    db = SessionLocal()
    
    # Create workspace + app
    ws = Workspace(name="Test WS2", slug=f"test-quota-2-{uuid.uuid4().hex[:6]}")
    db.add(ws)
    db.commit()
    
    app = Application(workspace_id=ws.id, name="Test App")
    db.add(app)
    db.commit()

    key = APIKey(application_id=app.id, key_hash="testhash123", key_prefix="mg_test")
    db.add(key)
    db.commit()

    # Create quota: 100 tokens daily
    policy = QuotaPolicy(
        scope_type="workspace",
        scope_id=ws.id,
        quota_tokens=100,
        quota_used_tokens=150,
        quota_reset_policy="daily"
    )
    db.add(policy)
    db.commit()
    
    req = Request(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        application_id=app.id,
        api_key_id=key.id,
        model_requested="demo-gpt-3.5-turbo",
        model_actual="demo-gpt-3.5-turbo",
        status_code=200,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    db.add(req)
    db.commit()

    # Add usage record: 150 tokens (over limit)
    usage = UsageRecord(
        request_id=req.id,
        workspace_id=ws.id,
        application_id=app.id,
        total_tokens=150,
        usage_source="TEST",
        created_at=datetime.utcnow()
    )
    db.add(usage)
    db.commit()
    
    # Check quota
    allowed, info = quota_enforcer.check_quota(
        db=db,
        workspace_id=ws.id
    )
    
    assert not allowed
    assert info["used"] == 150
    assert info["remaining"] == 0
    
    # Cleanup
    db.delete(usage)
    db.delete(policy)
    db.delete(app)
    db.delete(ws)
    db.commit()
    db.close()
