import json
from datetime import datetime
from app.ai.repository import AISummaryRepository
from app.ai.llm_client import generate_summary
from app.ai.confidence import calculate_confidence
from app.voice.repository import TranscriptRepository

async def generate_ai_summary(db, interaction_id, tenant_id, doctor_id):
    transcript_repo = TranscriptRepository(db)
    summary_repo = AISummaryRepository(db)

    transcript = await transcript_repo.find_by_interaction(interaction_id)

    if not transcript:
        return None

    full_text = " ".join([s["text"] for s in transcript["segments"]])

    ai_output = await generate_summary(full_text)
    structured = json.loads(ai_output)

    confidence = calculate_confidence(full_text)

    summary = await summary_repo.create({
        "interaction_id": interaction_id,
        "tenant_id": tenant_id,
        "doctor_id": doctor_id,
        "summary": structured["summary"],
        "complaints": structured["complaints"],
        "action_points": structured["action_points"],
        "confidence_score": confidence,
        "model_version": "gpt-4.1-mini",
        "prompt_version": "v1",
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    })

    return summary
