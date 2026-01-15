from fastapi import APIRouter, Depends, HTTPException
from app.db.mongo import get_db
from app.auth.service import authenticate_user, generate_token

router = APIRouter()

@router.post("/login")
async def login(email: str, password: str):
    db = get_db()
    user = await authenticate_user(db, email, password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = await generate_token(db, user)
    return {"access_token": token, "token_type": "bearer"}
