from fastapi import APIRouter, Request, Depends, HTTPException
from app.db.mongo import get_db
from app.ai.service import generate_ai_summary
from app.roles.guard import require_permission

router = APIRouter()

@router.post("/summarize", dependencies=[Depends(require_permission("interaction:close"))])
async def summarize_interaction(request: Request, interaction_id: str):
    db = get_db()

    summary = await generate_ai_summary(
        db=db,
        interaction_id=interaction_id,
        tenant_id=request.state.tenant_id,
        doctor_id=request.state.user_id
    )

    if not summary:
        raise HTTPException(status_code=400, detail="No transcript found")

    return summary
