import secrets
from datetime import datetime, timedelta
from app.invites.repository import InviteRepository

INVITE_EXPIRY_HOURS = 48

async def create_invite(db, tenant_id: str, email: str, role_name: str):
    repo = InviteRepository(db)

    token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(hours=INVITE_EXPIRY_HOURS)).isoformat()

    invite = {
        "tenant_id": tenant_id,
        "email": email,
        "role_name": role_name,
        "token": token,
        "expires_at": expires_at,
        "status": "pending"
    }

    return await repo.create(invite)


async def accept_invite(db, token: str, password_hash: str):
    repo = InviteRepository(db)
    invite = await repo.find_by_token(token)

    if not invite:
        return None

    # Mark invite as used
    await repo.update({"_id": invite["_id"]}, {"status": "accepted"})

    return invite
