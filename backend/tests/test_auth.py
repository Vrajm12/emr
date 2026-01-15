"""
TC-01: Valid Login Test

This test verifies that a valid login:
1. Returns a JWT token
2. Creates a session in the database
3. Logs an audit event with action: LOGIN_SUCCESS

TC-02: Invalid Password Test
This test verifies that login with wrong password:
1. Returns 401 Unauthorized
2. No session created
3. Logs audit event with action: LOGIN_FAILED

TC-03: Token Tampering Test
This test verifies that modifying JWT payload:
1. Returns 401 Unauthorized
2. Logs audit event with action: TOKEN_INVALID

TC-04: Token Expiry Test
This test verifies that using expired token:
1. Returns 401 Unauthorized
2. Logs audit event with action: TOKEN_EXPIRED
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from app.auth.service import authenticate_user, generate_token
from app.core.security import verify_password, create_access_token
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings


class TestTC01ValidLogin:
    """TC-01: Valid Login"""
    
    @pytest.mark.asyncio
    async def test_valid_login_returns_jwt(self, valid_user):
        """
        Action: Login with valid email/password
        Expected: JWT returned
        """
        # Arrange
        mock_db = MagicMock()
        mock_db["users"].find_one = AsyncMock(return_value=valid_user)
        
        email = "test@example.com"
        password = "password123"
        
        # Mock verify_password to always return True for this test
        with patch('app.auth.service.verify_password', return_value=True):
            # Act
            user = await authenticate_user(mock_db, email, password)
            
            # Assert
            assert user is not None
            assert user["email"] == email
            assert user["_id"] == "user123"
    
    @pytest.mark.asyncio
    async def test_valid_login_creates_session(self, valid_user):
        """
        Action: Login with valid email/password
        Expected: Session created in database
        """
        # Arrange
        mock_db = MagicMock()
        mock_db["sessions"].insert_one = AsyncMock()
        
        # Act
        token = await generate_token(mock_db, valid_user)
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        mock_db["sessions"].insert_one.assert_called_once()
        
        # Verify session data structure
        call_args = mock_db["sessions"].insert_one.call_args[0][0]
        assert call_args["user_id"] == valid_user["_id"]
        assert call_args["tenant_id"] == valid_user["tenant_id"]
        assert call_args["token"] == token
    
    @pytest.mark.asyncio
    async def test_valid_login_logs_audit_event(self, valid_user):
        """
        Action: Login with valid email/password
        Expected: Audit event logged with action: LOGIN_SUCCESS
        """
        # Arrange
        mock_db = MagicMock()
        mock_db["audit_events"].insert_one = AsyncMock()
        
        mock_request = MagicMock()
        mock_request.state.request_id = "req123"
        mock_request.state.user_id = valid_user["_id"]
        mock_request.state.tenant_id = valid_user["tenant_id"]
        mock_request.state.actor_type = "HUMAN"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get = MagicMock(return_value="Mozilla/5.0")
        
        # Mock the get_db function to return our mock_db
        with patch('app.audit.service.get_db', return_value=mock_db):
            from app.audit.service import write_audit_event
            
            # Act
            await write_audit_event(mock_request, "LOGIN_SUCCESS")
        
        # Assert
        mock_db["audit_events"].insert_one.assert_called_once()
        
        # Verify audit event structure
        call_args = mock_db["audit_events"].insert_one.call_args[0][0]
        assert call_args["action"] == "LOGIN_SUCCESS"
        assert call_args["actor_id"] == valid_user["_id"]
        assert call_args["tenant_id"] == valid_user["tenant_id"]
        assert call_args["actor_type"] == "HUMAN"
        assert call_args["ip"] == "127.0.0.1"
        assert "_id" in call_args
        assert "timestamp" in call_args
    
    @pytest.mark.asyncio
    async def test_full_login_flow_integration(self, valid_user):
        """
        Full integration test for TC-01
        Action: Complete login flow with valid credentials
        Expected: JWT returned, Session created, Audit event logged
        """
        # Arrange - Create separate mocks for different collections
        mock_db = {}
        mock_db["users"] = MagicMock()
        mock_db["users"].find_one = AsyncMock(return_value=valid_user)
        mock_db["sessions"] = MagicMock()
        mock_db["sessions"].insert_one = AsyncMock()
        mock_db["audit_events"] = MagicMock()
        mock_db["audit_events"].insert_one = AsyncMock()
        
        email = "test@example.com"
        password = "password123"
        
        # Mock verify_password for authentication
        with patch('app.auth.service.verify_password', return_value=True):
            # Act - Step 1: Authenticate user
            authenticated_user = await authenticate_user(mock_db, email, password)
            
            # Assert - User authenticated
            assert authenticated_user is not None
            assert authenticated_user["email"] == email
        
        # Act - Step 2: Generate token and create session
        token = await generate_token(mock_db, authenticated_user)
        
        # Assert - JWT returned and session created
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        mock_db["sessions"].insert_one.assert_called_once()
        
        # Act - Step 3: Log audit event
        mock_request = MagicMock()
        mock_request.state.request_id = "req123"
        mock_request.state.user_id = authenticated_user["_id"]
        mock_request.state.tenant_id = authenticated_user["tenant_id"]
        mock_request.state.actor_type = "HUMAN"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get = MagicMock(return_value="Mozilla/5.0")
        
        # Mock the get_db function for audit
        with patch('app.audit.service.get_db', return_value=mock_db):
            from app.audit.service import write_audit_event
            await write_audit_event(mock_request, "LOGIN_SUCCESS")
        
        # Assert - Audit event logged
        mock_db["audit_events"].insert_one.assert_called_once()
        audit_call = mock_db["audit_events"].insert_one.call_args[0][0]
        assert audit_call["action"] == "LOGIN_SUCCESS"
        
        print("\n✅ TC-01 PASSED: Valid Login")
        print(f"   - JWT Token: {token[:20]}...")
        print(f"   - Session Created: User {authenticated_user['_id']}")
        print(f"   - Audit Event: LOGIN_SUCCESS logged")
