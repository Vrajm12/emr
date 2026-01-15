from app.db.repository import BaseRepository

class TranscriptRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db["voice_transcripts"])

    async def find_by_interaction(self, interaction_id: str):
        return await self.find_one({"interaction_id": interaction_id})
