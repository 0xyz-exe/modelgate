"""Quota enforcement service"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.models import UsageRecord, QuotaPolicy


class QuotaEnforcer:
    """Enforce token quotas"""
    
    @staticmethod
    def check_quota(
        db: Session,
        workspace_id: str,
        application_id: str = None
    ) -> tuple[bool, dict]:
        """
        Check if request is within quota.
        
        Returns:
            (allowed: bool, info: dict)
        """
        # Get quota policy using scope_type/scope_id
        policy = None
        if application_id:
            policy = db.query(QuotaPolicy).filter(
                QuotaPolicy.scope_type == "application",
                QuotaPolicy.scope_id == application_id
            ).first()
        
        if not policy:
            # Check workspace-level policy
            policy = db.query(QuotaPolicy).filter(
                QuotaPolicy.scope_type == "workspace",
                QuotaPolicy.scope_id == workspace_id
            ).first()
        
        if not policy or not policy.quota_tokens:
            # No quota policy = unlimited
            return True, {"quota_enabled": False}
        
        # Check current usage against limit
        if policy.quota_used_tokens >= policy.quota_tokens:
            return False, {
                "quota_enabled": True,
                "limit": policy.quota_tokens,
                "used": policy.quota_used_tokens,
                "remaining": 0,
                "reset_policy": policy.quota_reset_policy
            }
        
        return True, {
            "quota_enabled": True,
            "limit": policy.quota_tokens,
            "used": policy.quota_used_tokens,
            "remaining": policy.quota_tokens - policy.quota_used_tokens,
            "reset_policy": policy.quota_reset_policy
        }


quota_enforcer = QuotaEnforcer()
