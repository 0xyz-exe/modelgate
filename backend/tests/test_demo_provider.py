"""Unit tests for demo provider"""
import pytest
from app.providers.demo import DemoProvider
from app.providers.base import ChatRequest, ChatMessage


@pytest.mark.asyncio
async def test_demo_provider_hello():
    """Test demo provider with hello message"""
    provider = DemoProvider()
    
    request = ChatRequest(
        model="gpt-3.5-turbo",
        messages=[
            ChatMessage(role="user", content="hello there")
        ]
    )
    
    response = await provider.chat_completion(request)
    
    assert response.id.startswith("demo_")
    assert response.model == "demo-gpt-3.5-turbo"
    assert "demo" in response.content.lower()
    assert response.prompt_tokens is not None
    assert response.completion_tokens is not None
    assert response.total_tokens == response.prompt_tokens + response.completion_tokens
    assert response.usage_source == "DEMO"
    assert response.finish_reason == "stop"


@pytest.mark.asyncio
async def test_demo_provider_test_keyword():
    """Test demo provider with test keyword"""
    provider = DemoProvider()
    
    request = ChatRequest(
        model="gpt-4",
        messages=[
            ChatMessage(role="user", content="this is a test")
        ]
    )
    
    response = await provider.chat_completion(request)
    
    assert "test" in response.content.lower()
    assert response.model == "demo-gpt-4"
    assert response.usage_source == "DEMO"


@pytest.mark.asyncio
async def test_demo_provider_generic():
    """Test demo provider with generic message"""
    provider = DemoProvider()
    
    request = ChatRequest(
        model="claude-3",
        messages=[
            ChatMessage(role="user", content="What is the weather?")
        ]
    )
    
    response = await provider.chat_completion(request)
    
    assert response.model == "demo-claude-3"
    assert "demo mode" in response.content.lower()
    assert response.usage_source == "DEMO"


@pytest.mark.asyncio
async def test_demo_provider_health():
    """Test demo provider health check"""
    provider = DemoProvider()
    
    health = await provider.health_check()
    
    assert health.status == "healthy"
    assert health.latency_ms == 1
    assert health.error is None


@pytest.mark.asyncio
async def test_demo_provider_token_counting():
    """Test that token counts are deterministic"""
    provider = DemoProvider()
    
    request1 = ChatRequest(
        model="test",
        messages=[ChatMessage(role="user", content="hello")]
    )
    request2 = ChatRequest(
        model="test",
        messages=[ChatMessage(role="user", content="hello")]
    )
    
    response1 = await provider.chat_completion(request1)
    response2 = await provider.chat_completion(request2)
    
    # Same input should give same token counts
    assert response1.prompt_tokens == response2.prompt_tokens
    assert response1.total_tokens > 0
