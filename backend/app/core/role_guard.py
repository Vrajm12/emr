from fastapi import Request, HTTPException, Depends

def require_role(allowed_roles: list):
    async def role_checker(request: Request):
        role_id = getattr(request.state, "role_id", None)

        if not role_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Later: map role_id to role name
        # For now, assume role_id itself is trusted

        if role_id not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")

        return True

    return role_checker
