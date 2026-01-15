from fastapi import Request, HTTPException

async def tenant_context_middleware(request: Request, call_next):
    # If route is public (like login), skip
    if request.url.path.startswith("/auth"):
        return await call_next(request)

    # Enforce tenant context for all other routes
    if not hasattr(request.state, "tenant_id"):
        raise HTTPException(status_code=403, detail="Tenant context missing")

    return await call_next(request)
