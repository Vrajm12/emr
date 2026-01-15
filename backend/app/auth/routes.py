from fastapi import APIRouter, Depends, HTTPException, Request
from app.db.mongo import get_db
from app.auth.service import authenticate_user, generate_token
from app.audit.service import write_audit_event

router = APIRouter()

@router.post("/login")
async def login(request: Request, email: str, password: str):
    db = get_db()
    user = await authenticate_user(db, email, password)

    if not user:
        # Log failed login audit event
        request.state.user_id = None
        request.state.tenant_id = None
        await write_audit_event(request, "LOGIN_FAILED")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = await generate_token(db, user)
    
    # Log successful login audit event
    request.state.user_id = user["_id"]
    request.state.tenant_id = user["tenant_id"]
    await write_audit_event(request, "LOGIN_SUCCESS")
    
    return {"access_token": token, "token_type": "bearer"}
