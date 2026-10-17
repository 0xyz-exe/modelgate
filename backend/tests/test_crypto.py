"""Unit tests for API key authentication"""
import pytest
from datetime import datetime, timedelta
from app.utils.crypto import generate_api_key, hash_api_key, get_key_prefix


def test_generate_api_key():
    """Test API key generation"""
    key = generate_api_key()
    
    assert key.startswith("mg_")
    assert len(key) > 10
    
    # Should be unique
    key2 = generate_api_key()
    assert key != key2


def test_hash_api_key():
    """Test API key hashing"""
    key = "mg_test123456"
    hash1 = hash_api_key(key)
    
    assert len(hash1) == 64  # SHA-256 hex
    assert hash1.isalnum()
    
    # Same input gives same hash
    hash2 = hash_api_key(key)
    assert hash1 == hash2
    
    # Different input gives different hash
    hash3 = hash_api_key("mg_different")
    assert hash1 != hash3


def test_get_key_prefix():
    """Test key prefix extraction"""
    key = "mg_abc123def"
    prefix = get_key_prefix(key)
    
    assert prefix == "mg_abc12"
    assert len(prefix) == 8
    
    # Short key
    short = "mg_12"
    assert get_key_prefix(short) == "mg_12"
