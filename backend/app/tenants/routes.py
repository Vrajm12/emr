from fastapi import APIRouter, Depends, HTTPException, Request
from app.tenants.service import create_tenant
from app.db.mongo import get_db
from app.roles.guard import require_permission

router = APIRouter()

@router.post("/create", dependencies=[Depends(require_permission("tenant:create"))])
async def create_new_tenant(
    request: Request,
    name: str,
    contact_email: str,
    admin_password: str
):
    db = get_db()

    result = await create_tenant(db, name, contact_email, admin_password)

    if not result:
        raise HTTPException(status_code=400, detail="Tenant already exists")

    return {
        "message": "Tenant created successfully",
        "tenant_id": result["tenant"]["_id"],
        "admin_email": result["admin_user"]["email"]
    }
