from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import register_middlewares
from app.auth.routes import router as auth_router
from app.audit.routes import router as audit_router
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.invites.routes import router as invite_router
from app.tenants.routes import router as tenant_router

def create_app():
    app = FastAPI(
        title="EMR Platform Core",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url=None
    )

    # Register security & control middleware (request-id, audit hook, etc.)
    register_middlewares(app)

    # Core routes (perimeter only)
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(audit_router, prefix="/audit", tags=["Audit"])
    app.include_router(invite_router, prefix="/invites", tags=["Invites"])
    app.include_router(tenant_router, prefix="/tenants", tags=["Tenants"])
    # Mongo lifecycle
    @app.on_event("startup")
    async def startup_event():
        await connect_to_mongo()

    @app.on_event("shutdown")
    async def shutdown_event():
        await close_mongo_connection()

    return app


app = create_app()
