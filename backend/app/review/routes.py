from fastapi import APIRouter, Request, Depends, HTTPException
from app.db.mongo import get_db
from app.review.service import approve_summary, reject_summary
from app.roles.guard import require_permission

router = APIRouter()

@router.post("/approve", dependencies=[Depends(require_permission("interaction:close"))])
async def approve_ai_summary(
    request: Request,
    summary_id: str,
    edited_summary: dict = None
):
    db = get_db()

    result = await approve_summary(
        db=db,
        summary_id=summary_id,
        doctor_id=request.state.user_id,
        edited_version=edited_summary
    )

    if not result:
        raise HTTPException(status_code=404, detail="Summary not found")

    return {"message": "Summary approved", "final_version": result}


@router.post("/reject", dependencies=[Depends(require_permission("interaction:close"))])
async def reject_ai_summary(
    request: Request,
    summary_id: str,
    reason: str
):
    db = get_db()

    await reject_summary(
        db=db,
        summary_id=summary_id,
        doctor_id=request.state.user_id,
        reason=reason
    )

    return {"message": "Summary rejected"}
