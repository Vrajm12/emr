from datetime import datetime
from app.ai.repository import AISummaryRepository

async def approve_summary(db, summary_id: str, doctor_id: str, edited_version: dict = None):
    repo = AISummaryRepository(db)

    summary = await repo.find_one({"_id": summary_id})

    if not summary:
        return None

    final_data = edited_version if edited_version else {
        "summary": summary["summary"],
        "complaints": summary["complaints"],
        "action_points": summary["action_points"]
    }

    await repo.update(
        {"_id": summary_id},
        {
            "status": "approved",
            "reviewed_by": doctor_id,
            "reviewed_at": datetime.utcnow().isoformat(),
            "final_version": final_data
        }
    )

    return final_data


async def reject_summary(db, summary_id: str, doctor_id: str, reason: str):
    repo = AISummaryRepository(db)

    await repo.update(
        {"_id": summary_id},
        {
            "status": "rejected",
            "reviewed_by": doctor_id,
            "reviewed_at": datetime.utcnow().isoformat(),
            "rejection_reason": reason
        }
    )
