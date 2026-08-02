from pydantic import BaseModel

class TranscriptionRequestSchema(BaseModel):
    request_id : str
    audio_url : str
    extension : str