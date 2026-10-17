"""Unit tests for quota enforcement"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Workspace, Application, QuotaPolicy, UsageRecord
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
    ws = Workspace(name="Test WS", slug="test-quota-1")
    db.add(ws)
    db.commit()
    
    # Create quota policy: 1000 tokens daily
    policy = QuotaPolicy(
        workspace_id=ws.id,
        policy_type="token",
        limit_value=1000,
        period="daily",
        enabled=True
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
    ws = Workspace(name="Test WS2", slug="test-quota-2")
    db.add(ws)
    db.commit()
    
    app = Application(workspace_id=ws.id, name="Test App")
    db.add(app)
    db.commit()
    
    # Create quota: 100 tokens daily
    policy = QuotaPolicy(
        workspace_id=ws.id,
        policy_type="token",
        limit_value=100,
        period="daily",
        enabled=True
    )
    db.add(policy)
    db.commit()
    
    # Add usage record: 150 tokens (over limit)
    usage = UsageRecord(
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
