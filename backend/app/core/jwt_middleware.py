from fastapi import Request, HTTPException
from jose import jwt, JWTError
from app.core.config import settings

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
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Attach identity to request context
        request.state.user_id = payload.get("user_id")
        request.state.tenant_id = payload.get("tenant_id")
        request.state.role_id = payload.get("role_id")
        request.state.role_name = payload.get("role_name")
        request.state.actor_type = "HUMAN"

        if not request.state.user_id or not request.state.tenant_id:
            raise HTTPException(status_code=401, detail="Invalid token")

    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return await call_next(request)
