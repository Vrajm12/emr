from fastapi import Request, HTTPException, Depends
from app.roles.service import has_permission

def require_permission(permission: str):
    async def permission_checker(request: Request):
        role_name = getattr(request.state, "role_name", None)

        if not role_name:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not has_permission(role_name, permission):
            raise HTTPException(status_code=403, detail="Permission denied")

        return True

    return permission_checker
