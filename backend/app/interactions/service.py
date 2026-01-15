from datetime import datetime
from app.interactions.repository import InteractionRepository

async def start_interaction(db, tenant_id: str, doctor_id: str):
    repo = InteractionRepository(db)

    # Prevent parallel sessions
    existing = await repo.find_active_by_doctor(doctor_id, tenant_id)
    if existing:
        return existing

    interaction = await repo.create({
        "tenant_id": tenant_id,
        "doctor_id": doctor_id,
        "status": "active",
        "started_at": datetime.utcnow().isoformat(),
        "ended_at": None,
        "notes": None,
        "ai_summary": None
    })

    return interaction


async def close_interaction(db, interaction_id: str):
    repo = InteractionRepository(db)

    await repo.update(
        {"_id": interaction_id},
        {
            "status": "completed",
            "ended_at": datetime.utcnow().isoformat()
        }
    )
