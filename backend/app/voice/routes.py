from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.voice.whisper_engine import transcribe_audio
from app.voice.service import append_transcript_segment
from app.db.mongo import get_db
import tempfile
import os

router = APIRouter()

@router.websocket("/stream/{interaction_id}")
async def voice_stream(websocket: WebSocket, interaction_id: str):
    await websocket.accept()

    try:
        while True:
            audio_bytes = await websocket.receive_bytes()

            # Save chunk temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                temp_path = f.name

            # Transcribe
            text = transcribe_audio(temp_path)

            # Cleanup
            os.remove(temp_path)

            # Store transcript
            db = get_db()
            await append_transcript_segment(
                db=db,
                interaction_id=interaction_id,
                tenant_id=websocket.scope["state"].tenant_id,
                doctor_id=websocket.scope["state"].user_id,
                text=text
            )

            # Send back live text
            await websocket.send_json({"text": text})

    except WebSocketDisconnect:
        print("Voice stream closed")
