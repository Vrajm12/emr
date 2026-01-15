from datetime import datetime
from app.voice.repository import TranscriptRepository

async def append_transcript_segment(
    db,
    interaction_id: str,
    tenant_id: str,
    doctor_id: str,
    text: str
):
    repo = TranscriptRepository(db)

    transcript = await repo.find_by_interaction(interaction_id)

    segment = {
        "timestamp": datetime.utcnow().isoformat(),
        "text": text
    }

    if not transcript:
        await repo.create({
            "interaction_id": interaction_id,
            "tenant_id": tenant_id,
            "doctor_id": doctor_id,
            "segments": [segment]
        })
    else:
        transcript["segments"].append(segment)
        await repo.update({"_id": transcript["_id"]}, {"segments": transcript["segments"]})
