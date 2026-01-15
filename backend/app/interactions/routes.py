from fastapi import APIRouter, Request, Depends, HTTPException
from app.db.mongo import get_db
from app.interactions.service import start_interaction, close_interaction
from app.roles.guard import require_permission

router = APIRouter()

@router.post("/start", dependencies=[Depends(require_permission("interaction:start"))])
async def start_session(request: Request):
    db = get_db()

    interaction = await start_interaction(
        db=db,
        tenant_id=request.state.tenant_id,
        doctor_id=request.state.user_id
    )

    return {"interaction_id": interaction["_id"]}


@router.post("/close", dependencies=[Depends(require_permission("interaction:close"))])
async def close_session(interaction_id: str):
    db = get_db()
    await close_interaction(db, interaction_id)
    return {"message": "Interaction closed"}
