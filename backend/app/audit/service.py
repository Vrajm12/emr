import uuid
from datetime import datetime
from app.db.mongo import get_db

async def write_audit_event(request, action: str):
    db = get_db()
    audit_event = {
        "_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request.state.request_id,
        "actor_id": getattr(request.state, "user_id", None),
        "actor_type": getattr(request.state, "actor_type", "HUMAN"),
        "tenant_id": getattr(request.state, "tenant_id", None),
        "action": action,
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }

    await db["audit_events"].insert_one(audit_event)
