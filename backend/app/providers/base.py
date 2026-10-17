"""Base provider interface"""
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class ChatResponse(BaseModel):
    id: str
    model: str
    content: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    usage_source: str = "UNKNOWN"
    finish_reason: str = "stop"


class ProviderHealth(BaseModel):
    status: str  # healthy, degraded, down
    latency_ms: Optional[int] = None
    error: Optional[str] = None


class ProviderAdapter(ABC):
    """Abstract provider interface"""

    @abstractmethod
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Send chat completion request"""
        pass

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Check provider health"""
        pass
