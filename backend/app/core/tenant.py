"""
Helper function to validate tenant access
"""
from fastapi import HTTPException, Request
from app.audit.service import write_audit_event


async def validate_tenant_access(request: Request, resource_tenant_id: str):
    """
    Validates that the requesting user's tenant matches the resource's tenant.
    
    Args:
        request: FastAPI request object with tenant_id in state
        resource_tenant_id: The tenant_id of the resource being accessed
        
    Raises:
        HTTPException: 403 if tenant mismatch detected
    """
    request_tenant_id = getattr(request.state, "tenant_id", None)
    
    if not request_tenant_id:
        raise HTTPException(status_code=403, detail="Tenant context missing")
    
    if request_tenant_id != resource_tenant_id:
        # Log cross-tenant access attempt
        await write_audit_event(request, "CROSS_TENANT_ACCESS_ATTEMPT")
        raise HTTPException(
            status_code=403, 
            detail="Access denied: Cross-tenant access not allowed"
        )
    
    return True
