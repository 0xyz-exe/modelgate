"""Cryptography utilities"""
import hashlib
import secrets


def hash_api_key(key: str) -> str:
    """SHA-256 hash of API key"""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> str:
    """Generate cryptographically secure API key"""
    # mg_ prefix + 32 random chars
    random_part = secrets.token_urlsafe(24)  # ~32 chars after encoding
    return f"mg_{random_part}"


def get_key_prefix(key: str) -> str:
    """Extract displayable prefix (first 8 chars)"""
    return key[:8] if len(key) >= 8 else key
