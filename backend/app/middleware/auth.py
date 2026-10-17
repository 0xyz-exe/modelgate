"""Auth middleware"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import APIKey, Application, Workspace
from app.utils.crypto import hash_api_key
from datetime import datetime


class AuthContext:
    def __init__(self, api_key: APIKey, application: Application, workspace: Workspace):
        self.api_key = api_key
        self.application = application
        self.workspace = workspace


async def get_auth_context(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> AuthContext:
    """Authenticate API key and return context"""
    # Extract token from "Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization[7:]  # Remove "Bearer "
    
    # Hash and lookup
    key_hash = hash_api_key(token)
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check revoked
    if api_key.revoked_at:
        raise HTTPException(status_code=401, detail="API key revoked")
    
    # Check expired
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API key expired")
    
    # Load related objects
    application = db.query(Application).filter(Application.id == api_key.application_id).first()
    if not application:
        raise HTTPException(status_code=500, detail="Application not found")
    
    workspace = db.query(Workspace).filter(Workspace.id == application.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=500, detail="Workspace not found")
    
    # Update last used
    api_key.last_used_at = datetime.utcnow()
    db.commit()
    
    return AuthContext(api_key=api_key, application=application, workspace=workspace)
