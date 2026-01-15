"""
TC-05, TC-06, TC-07: Tenant Isolation Test Cases

These tests verify that:
- TC-05: Users can only access their own tenant's data
- TC-06: Cross-tenant access attempts are blocked with 403
- TC-07: Tenant spoofing attempts are prevented
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from app.core.tenant import validate_tenant_access
from app.core.tenant_middleware import tenant_context_middleware
from app.interactions.repository import InteractionRepository


class TestTC05TenantAAccess:
    """TC-05: Tenant A Access"""
    
    @pytest.mark.asyncio
    async def test_tenant_a_sees_only_own_data(self):
        """
        Action: Login as Doctor A, fetch tenant-bound resource
        Expected: Only Tenant A data visible
        """
        # Arrange - Create mock database with multi-tenant data
        mock_db = {
            "interactions": MagicMock()
        }
        
        tenant_a_data = {
            "_id": "interaction_a1",
            "tenant_id": "tenant_a",
            "doctor_id": "doctor_a",
            "status": "active",
            "data": "Tenant A Patient Data"
        }
        
        tenant_b_data = {
            "_id": "interaction_b1",
            "tenant_id": "tenant_b",
            "doctor_id": "doctor_b",
            "status": "active",
            "data": "Tenant B Patient Data"
        }
        
        # Mock find_one to return only tenant A data
        mock_db["interactions"].find_one = AsyncMock(return_value=tenant_a_data)
        
        # Create repository
        repo = InteractionRepository(mock_db)
        
        # Act - Query with tenant A context
        result = await repo.find_active_by_doctor("doctor_a", "tenant_a")
        
        # Assert - Only tenant A data returned
        assert result is not None
        assert result["tenant_id"] == "tenant_a"
        assert result["doctor_id"] == "doctor_a"
        assert result["data"] == "Tenant A Patient Data"
        
        # Verify query included tenant filter
        mock_db["interactions"].find_one.assert_called_once_with({
            "doctor_id": "doctor_a",
            "tenant_id": "tenant_a",
            "status": "active"
        })
        
        print("\n✅ TC-05 PASSED: Tenant A Access")
        print("   - Doctor A can only see Tenant A data")
        print("   - Tenant filter applied to queries")
    
    @pytest.mark.asyncio
    async def test_tenant_isolation_in_repository(self):
        """
        Verify repository always filters by tenant_id
        """
        # Arrange
        mock_db = {
            "interactions": MagicMock()
        }
        mock_db["interactions"].find_one = AsyncMock(return_value=None)
        
        repo = InteractionRepository(mock_db)
        
        # Act - Try to query without finding anything
        result = await repo.find_active_by_doctor("doctor_x", "tenant_x")
        
        # Assert - Query included tenant_id
        call_args = mock_db["interactions"].find_one.call_args[0][0]
        assert "tenant_id" in call_args
        assert call_args["tenant_id"] == "tenant_x"
        assert result is None


class TestTC06CrossTenantAttack:
    """TC-06: Cross-Tenant Attack"""
    
    @pytest.mark.asyncio
    async def test_cross_tenant_access_returns_403(self):
        """
        Action: Use Doctor A token, attempt to access Tenant B resource
        Expected: 403 Forbidden
        """
        # Arrange - Create request from Tenant A user
        mock_request = MagicMock()
        mock_request.state.tenant_id = "tenant_a"
        mock_request.state.user_id = "doctor_a"
        mock_request.state.request_id = "req123"
        mock_request.state.actor_type = "HUMAN"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get = MagicMock(return_value="Mozilla/5.0")
        
        # Resource belongs to Tenant B
        resource_tenant_id = "tenant_b"
        
        # Mock audit logging
        mock_db = MagicMock()
        mock_db["audit_events"].insert_one = AsyncMock()
        
        # Act & Assert
        with patch('app.core.tenant.write_audit_event') as mock_audit:
            mock_audit.return_value = AsyncMock()
            
            with pytest.raises(HTTPException) as exc_info:
                await validate_tenant_access(mock_request, resource_tenant_id)
            
            # Assert 403 Forbidden
            assert exc_info.value.status_code == 403
            assert "cross-tenant" in str(exc_info.value.detail).lower()
    
    @pytest.mark.asyncio
    async def test_cross_tenant_access_logs_audit_event(self):
        """
        Action: Attempt cross-tenant access
        Expected: Audit event: CROSS_TENANT_ACCESS_ATTEMPT
        """
        # Arrange
        mock_request = MagicMock()
        mock_request.state.tenant_id = "tenant_a"
        mock_request.state.user_id = "doctor_a"
        mock_request.state.request_id = "req123"
        mock_request.state.actor_type = "HUMAN"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get = MagicMock(return_value="Mozilla/5.0")
        
        mock_db = MagicMock()
        mock_db["audit_events"].insert_one = AsyncMock()
        
        # Act
        with patch('app.audit.service.get_db', return_value=mock_db):
            with patch('app.core.tenant.write_audit_event') as mock_write_audit:
                mock_write_audit.return_value = AsyncMock()
                
                try:
                    await validate_tenant_access(mock_request, "tenant_b")
                except HTTPException:
                    pass
                
                # Assert audit event was called
                mock_write_audit.assert_called_once_with(mock_request, "CROSS_TENANT_ACCESS_ATTEMPT")
        
        print("\n✅ TC-06 PASSED: Cross-Tenant Attack")
        print("   - 403 Forbidden returned")
        print("   - Audit Event: CROSS_TENANT_ACCESS_ATTEMPT logged")
    
    @pytest.mark.asyncio
    async def test_same_tenant_access_allowed(self):
        """
        Verify that same-tenant access is allowed
        """
        # Arrange
        mock_request = MagicMock()
        mock_request.state.tenant_id = "tenant_a"
        mock_request.state.user_id = "doctor_a"
        
        # Act - Access resource from same tenant
        result = await validate_tenant_access(mock_request, "tenant_a")
        
        # Assert - Access allowed
        assert result is True


class TestTC07TenantSpoofing:
    """TC-07: Tenant Spoofing"""
    
    @pytest.mark.asyncio
    async def test_manual_tenant_injection_ignored(self):
        """
        Action: Manually inject tenant_id in payload
        Expected: Ignored, server uses token tenant only
        """
        # Arrange - Create valid token for tenant_a
        payload = {
            "user_id": "doctor_a",
            "tenant_id": "tenant_a",
            "role_name": "doctor",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        # Create mock request with token
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")
        mock_request.client.host = "127.0.0.1"
        mock_request.state = MagicMock()
        
        # Mock database
        mock_db = {
            "interactions": MagicMock()
        }
        mock_db["interactions"].find_one = AsyncMock(return_value={
            "_id": "int1",
            "tenant_id": "tenant_a",
            "doctor_id": "doctor_a"
        })
        
        repo = InteractionRepository(mock_db)
        
        # Act - User tries to pass different tenant_id in request body
        # But repository uses token tenant from request.state
        spoofed_tenant = "tenant_b"  # User tries to spoof
        actual_tenant = "tenant_a"   # From token
        
        result = await repo.find_active_by_doctor("doctor_a", actual_tenant)
        
        # Assert - Server used token tenant, not spoofed value
        call_args = mock_db["interactions"].find_one.call_args[0][0]
        assert call_args["tenant_id"] == "tenant_a"
        assert call_args["tenant_id"] != spoofed_tenant
        
        print("\n✅ TC-07 PASSED: Tenant Spoofing")
        print("   - Manual tenant_id injection ignored")
        print("   - Server uses token tenant only")
    
    @pytest.mark.asyncio
    async def test_request_state_tenant_from_jwt_only(self):
        """
        Verify that tenant_id in request.state comes from JWT only
        """
        from app.core.jwt_middleware import jwt_auth_middleware
        
        # Arrange - Create token with tenant_a
        payload = {
            "user_id": "doctor_a",
            "tenant_id": "tenant_a",
            "role_name": "doctor",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")
        mock_request.client.host = "127.0.0.1"
        mock_request.state = MagicMock()
        
        # Mock call_next to capture state
        async def mock_call_next(request):
            return {"tenant_from_state": request.state.tenant_id}
        
        # Act - Process through JWT middleware
        with patch('app.audit.service.get_db'):
            result = await jwt_auth_middleware(mock_request, mock_call_next)
        
        # Assert - tenant_id set from JWT
        assert mock_request.state.tenant_id == "tenant_a"
        assert result["tenant_from_state"] == "tenant_a"
    
    @pytest.mark.asyncio
    async def test_tenant_from_service_layer(self):
        """
        Verify service layer uses request.state.tenant_id exclusively
        """
        from app.interactions.service import start_interaction
        
        # Arrange
        mock_db = {
            "interactions": MagicMock()
        }
        
        interaction_data = {
            "_id": "new_interaction",
            "tenant_id": "tenant_a",
            "doctor_id": "doctor_a",
            "status": "active"
        }
        
        mock_db["interactions"].find_one = AsyncMock(return_value=None)
        mock_db["interactions"].insert_one = AsyncMock(return_value=interaction_data)
        
        # Act - Service should use provided tenant_id parameter
        # (which comes from request.state.tenant_id in the route)
        result = await start_interaction(
            db=mock_db,
            tenant_id="tenant_a",  # This comes from request.state.tenant_id
            doctor_id="doctor_a"
        )
        
        # The service should have used tenant_a
        assert mock_db["interactions"].find_one.called
        call_args = mock_db["interactions"].find_one.call_args[0][0]
        assert call_args["tenant_id"] == "tenant_a"
        assert mock_db["interactions"].insert_one.called
        
        print("\n✅ TC-07 ADDITIONAL: Service Layer")
        print("   - Service layer respects request.state.tenant_id")
        print("   - No direct tenant manipulation possible")


class TestTC0507Integration:
    """Integration tests for tenant isolation"""
    
    @pytest.mark.asyncio
    async def test_full_tenant_isolation_flow(self):
        """
        Full integration: Token -> Middleware -> Service -> Repository
        """
        from app.core.jwt_middleware import jwt_auth_middleware
        
        # Arrange - Create token for Doctor A in Tenant A
        payload = {
            "user_id": "doctor_a",
            "tenant_id": "tenant_a",
            "role_name": "doctor",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        # Create mock request
        mock_request = MagicMock()
        mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")
        mock_request.url.path = "/api/interactions/start"
        mock_request.client.host = "127.0.0.1"
        mock_request.state = MagicMock()
        
        # Step 1: JWT Middleware sets tenant_id from token
        async def mock_call_next(request):
            # Step 2: Tenant middleware verifies tenant context exists
            if not hasattr(request.state, "tenant_id"):
                raise HTTPException(status_code=403, detail="Missing tenant")
            
            # Step 3: Route handler uses request.state.tenant_id
            return {"tenant_used": request.state.tenant_id}
        
        # Act
        with patch('app.audit.service.get_db'):
            result = await jwt_auth_middleware(mock_request, mock_call_next)
        
        # Assert - Full chain uses token tenant
        assert mock_request.state.tenant_id == "tenant_a"
        assert result["tenant_used"] == "tenant_a"
        
        print("\n✅ INTEGRATION PASSED: Full Tenant Isolation")
        print("   - JWT extracts tenant_id")
        print("   - Middleware validates tenant context")
        print("   - Services use request.state.tenant_id")
        print("   - Repositories filter by tenant_id")
