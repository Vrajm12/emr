from fastapi import FastAPI
from app.core.jwt_middleware import jwt_auth_middleware
from app.core.tenant_middleware import tenant_context_middleware
from uuid import uuid4
from app.audit.service import write_audit_event

def register_middlewares(app: FastAPI):

    @app.middleware("http")
    async def request_id_middleware(request, call_next):
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.middleware("http")
    async def jwt_middleware(request, call_next):
        return await jwt_auth_middleware(request, call_next)

    @app.middleware("http")
    async def tenant_middleware(request, call_next):
        return await tenant_context_middleware(request, call_next)

    @app.middleware("http")
    async def audit_middleware(request, call_next):
        response = await call_next(request)

        if hasattr(request.state, "user_id"):
            await write_audit_event(
                request=request,
                action=f"{request.method} {request.url.path}"
            )

        return response
