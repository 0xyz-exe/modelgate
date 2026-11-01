"""Integration tests for chat endpoint"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import SessionLocal
from app.db.models import Workspace, Application, APIKey
from app.utils.crypto import generate_api_key, hash_api_key, get_key_prefix


@pytest.fixture
def test_api_key():
    """Create a test API key"""
    db = SessionLocal()
    
    # Get or create demo workspace
    workspace = db.query(Workspace).filter(Workspace.slug == "demo").first()
    if not workspace:
        workspace = Workspace(name="Test Workspace", slug="demo")
        db.add(workspace)
        db.flush()
    
    # Get or create application
    application = db.query(Application).filter(
        Application.workspace_id == workspace.id
    ).first()
    if not application:
        application = Application(
            workspace_id=workspace.id,
            name="Test Application"
        )
        db.add(application)
        db.flush()
    
    # Create test API key
    key = generate_api_key()
    api_key = APIKey(
        application_id=application.id,
        key_hash=hash_api_key(key),
        key_prefix=get_key_prefix(key),
    )
    db.add(api_key)
    db.commit()
    
    yield key
    
    # Cleanup
    db.delete(api_key)
    db.commit()
    db.close()


@pytest.mark.asyncio
async def test_chat_completion_success(test_api_key):
    """Test successful chat completion"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/v1/chat/completions",
            headers={"Authorization": f"Bearer {test_api_key}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert data["object"] == "chat.completion"
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert "usage" in data
    assert data["usage"]["source"] == "DEMO"


@pytest.mark.asyncio
async def test_chat_completion_no_auth():
    """Test chat completion without authentication"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/v1/chat/completions",
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
    
    assert response.status_code == 422  # Missing header


@pytest.mark.asyncio
async def test_chat_completion_invalid_key():
    """Test chat completion with invalid key"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/v1/chat/completions",
            headers={"Authorization": "Bearer mg_invalid"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_completion_invalid_request(test_api_key):
    """Test chat completion with invalid request"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/v1/chat/completions",
            headers={"Authorization": f"Bearer {test_api_key}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": "invalid"  # Should be array
            }
        )
    
    assert response.status_code == 422  # Validation error
