import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

# Load test environment variables
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["POSTGRES_URL"] = "postgresql://test:test@localhost/test"
os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["OPENAI_API_KEY"] = "sk-test-key"
os.environ["MONGO_DB_NAME"] = "test_db"

from app.main import app
from app.db.mongo import get_db

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = MagicMock()
    db["users"] = MagicMock()
    db["sessions"] = MagicMock()
    db["audit_events"] = MagicMock()
    
    # Make insert_one async
    db["sessions"].insert_one = AsyncMock()
    db["audit_events"].insert_one = AsyncMock()
    
    return db

@pytest.fixture
def valid_user():
    """Sample valid user data with a fixed password hash"""
    # Pre-generated bcrypt hash for "password123"
    # Generated with: bcrypt.hashpw(b"password123", bcrypt.gensalt())
    return {
        "_id": "user123",
        "email": "test@example.com",
        "password_hash": "$2b$12$KIXqZ7KdKE.zHJBGvOh.JeO3YqL8Gm4O5VLrFWxY8Ks2XgGLZO2RK",
        "tenant_id": "tenant123",
        "role_name": "doctor",
        "first_name": "John",
        "last_name": "Doe"
    }
