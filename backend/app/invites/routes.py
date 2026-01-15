from fastapi import APIRouter, Depends, HTTPException, Request
from app.invites.service import create_invite, accept_invite
from app.db.mongo import get_db
from app.roles.guard import require_permission
from app.core.security import hash_password
from app.users.repository import UserRepository

router = APIRouter()

# Admin creates invite
@router.post("/create", dependencies=[Depends(require_permission("user:create"))])
async def invite_user(request: Request, email: str, role_name: str):
    db = get_db()
    tenant_id = request.state.tenant_id

    invite = await create_invite(db, tenant_id, email, role_name)

    # In real system: send email/WhatsApp here
    return {
        "message": "Invite created",
        "invite_token": invite["token"]
    }


# User accepts invite
@router.post("/accept")
async def accept_user_invite(token: str, password: str):
    db = get_db()

    password_hash = hash_password(password)
    invite = await accept_invite(db, token, password_hash)

    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite")

    user_repo = UserRepository(db)

    user = await user_repo.create({
        "tenant_id": invite["tenant_id"],
        "email": invite["email"],
        "password_hash": password_hash,
        "role_name": invite["role_name"],
        "is_active": True
    })

    return {"message": "Account created successfully"}
