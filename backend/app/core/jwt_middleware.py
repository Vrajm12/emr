from fastapi import Request, HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
from app.audit.service import write_audit_event

async def jwt_auth_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return await call_next(request)  # Public routes allowed

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Attach identity to request context
        request.state.user_id = payload.get("user_id")
        request.state.tenant_id = payload.get("tenant_id")
        request.state.role_id = payload.get("role_id")
        request.state.role_name = payload.get("role_name")
        request.state.actor_type = "HUMAN"

        if not request.state.user_id or not request.state.tenant_id:
            request.state.user_id = None
            request.state.tenant_id = None
            await write_audit_event(request, "TOKEN_INVALID")
            raise HTTPException(status_code=401, detail="Invalid token")

    except ExpiredSignatureError:
        request.state.user_id = None
        request.state.tenant_id = None
        await write_audit_event(request, "TOKEN_EXPIRED")
        raise HTTPException(status_code=401, detail="Token expired")
    except (JWTError, ValueError):
        request.state.user_id = None
        request.state.tenant_id = None
        await write_audit_event(request, "TOKEN_INVALID")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return await call_next(request)
