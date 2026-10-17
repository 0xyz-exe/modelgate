"""Chat completion endpoint"""
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.middleware.auth import get_auth_context, AuthContext
from app.middleware.rate_limit import check_rate_limit
from app.models.request import ChatCompletionRequest, ChatCompletionResponse, Choice, ChatMessage, UsageInfo
from app.providers.demo import DemoProvider
from app.providers.base import ChatRequest
from app.db.models import Request, UsageRecord
from app.services.quota import quota_enforcer
import time

router = APIRouter()


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(
    response: Response,
    request: ChatCompletionRequest,
    auth: AuthContext = Depends(get_auth_context),
    rate_limit_info: dict = Depends(check_rate_limit),
    db: Session = Depends(get_db),
):
    """Chat completion endpoint"""
    start_time = time.time()
    started_at = datetime.utcnow()
    
    # Add rate limit headers to response
    response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset"])
    
    # Check quota
    quota_allowed, quota_info = quota_enforcer.check_quota(
        db=db,
        workspace_id=auth.workspace.id,
        application_id=auth.application.id
    )
    
    if not quota_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": {
                    "type": "quota_exceeded",
                    "code": "quota_limit_exceeded",
                    "message": f"Token quota exceeded: {quota_info['used']}/{quota_info['limit']} tokens used",
                    "quota": quota_info
                }
            }
        )
    
    # Use demo provider for MVP
    provider = DemoProvider()
    
    # Convert to provider format
    from app.providers.base import ChatMessage as ProviderMessage
    provider_request = ChatRequest(
        model=request.model,
        messages=[ProviderMessage(role=m.role, content=m.content) for m in request.messages],
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    
    try:
        # Call provider
        provider_response = await provider.chat_completion(provider_request)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        completed_at = datetime.utcnow()
        
        # Record request
        db_request = Request(
            workspace_id=auth.workspace.id,
            application_id=auth.application.id,
            api_key_id=auth.api_key.id,
            model_requested=request.model,
            model_actual=provider_response.model,
            provider_id=None,  # Demo provider not in DB yet
            status_code=200,
            started_at=started_at,
            completed_at=completed_at,
            latency_ms=latency_ms,
            retry_count=0,
        )
        db.add(db_request)
        db.flush()  # Get request.id
        
        # Record usage
        usage_record = UsageRecord(
            request_id=db_request.id,
            workspace_id=auth.workspace.id,
            application_id=auth.application.id,
            input_tokens=provider_response.prompt_tokens,
            output_tokens=provider_response.completion_tokens,
            total_tokens=provider_response.total_tokens,
            usage_source=provider_response.usage_source,
        )
        db.add(usage_record)
        db.commit()
        
        # Return OpenAI-compatible response
        return ChatCompletionResponse(
            id=provider_response.id,
            created=int(started_at.timestamp()),
            model=provider_response.model,
            choices=[
                Choice(
                    message=ChatMessage(role="assistant", content=provider_response.content),
                    finish_reason=provider_response.finish_reason,
                )
            ],
            usage=UsageInfo(
                prompt_tokens=provider_response.prompt_tokens,
                completion_tokens=provider_response.completion_tokens,
                total_tokens=provider_response.total_tokens,
                source=provider_response.usage_source,
            ),
        )
        
    except Exception as e:
        import traceback
        # Record failed request
        error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        db_request = Request(
            workspace_id=auth.workspace.id,
            application_id=auth.application.id,
            api_key_id=auth.api_key.id,
            model_requested=request.model,
            status_code=500,
            started_at=started_at,
            completed_at=datetime.utcnow(),
            latency_ms=int((time.time() - start_time) * 1000),
            error_type="provider_error",
            error_message=error_detail[:500],  # Truncate for DB
        )
        db.add(db_request)
        db.commit()
        print(f"ERROR in chat completion: {error_detail}")
        raise
