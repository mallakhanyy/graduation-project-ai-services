from fastapi import FastAPI
from api.routes.transcription import router as transcription_router

app = FastAPI(
    title="ASR AI Service",
)

app.include_router(transcription_router)