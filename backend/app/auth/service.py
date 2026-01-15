from app.core.security import verify_password, create_access_token
from app.users.repository import UserRepository
from app.auth.session_repository import SessionRepository

async def authenticate_user(db, email: str, password: str):
    repo = UserRepository(db)
    user = await repo.find_by_email(email)

    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user

async def generate_token(db, user: dict):
    token_data = {
        "user_id": user["_id"],
        "tenant_id": user["tenant_id"],
        "role_name": user["role_name"]  # store role name directly
    }

    token = create_access_token(token_data)

    session_repo = SessionRepository(db)
    await session_repo.create({
        "user_id": user["_id"],
        "tenant_id": user["tenant_id"],
        "token": token
    })

    return token
