"""Demo provider - deterministic mock responses"""
import uuid
from app.providers.base import (
    ProviderAdapter,
    ChatRequest,
    ChatResponse,
    ProviderHealth,
)


class DemoProvider(ProviderAdapter):
    """Demo provider for testing without real API calls"""

    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Return deterministic response"""
        # Extract user message for deterministic response
        user_msg = next((m.content for m in request.messages if m.role == "user"), "")
        
        # Simple deterministic response logic
        if "hello" in user_msg.lower():
            content = "Hello! I'm a demo AI assistant. This is a simulated response."
        elif "test" in user_msg.lower():
            content = "Test response received. This is demo mode - no real API call was made."
        else:
            content = f"Demo response to: {user_msg[:50]}... (Demo mode active)"

        # Deterministic token counts
        input_tokens = sum(len(m.content.split()) * 1.3 for m in request.messages)
        output_tokens = len(content.split()) * 1.3

        return ChatResponse(
            id=f"demo_{uuid.uuid4().hex[:16]}",
            model=f"demo-{request.model}",
            content=content,
            prompt_tokens=int(input_tokens),
            completion_tokens=int(output_tokens),
            total_tokens=int(input_tokens + output_tokens),
            usage_source="DEMO",
            finish_reason="stop",
        )

    async def health_check(self) -> ProviderHealth:
        """Demo provider always healthy"""
        return ProviderHealth(status="healthy", latency_ms=1)
