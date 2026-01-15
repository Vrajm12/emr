from fastapi import APIRouter, Depends, Request
from app.roles.guard import require_permission

router = APIRouter()

@router.get("/events", dependencies=[Depends(require_permission("audit:view"))])
async def get_audit_events(request: Request):
    return {"message": "Audit events visible"}
