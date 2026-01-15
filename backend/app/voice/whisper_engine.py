import whisper

model = whisper.load_model("base")  # start with base, upgrade later

def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path)
    return result["text"]
