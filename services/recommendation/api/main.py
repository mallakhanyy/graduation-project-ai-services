from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes.recommendations import router as recommendations_router
from api.routes.ingestion import router as ingestion_router
from infrastructure.container import Container
from shared.config import get_settings


settings = get_settings()
container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await container.initialize()

    yield

    await container.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.state.container = container

app.include_router(recommendations_router)
app.include_router(ingestion_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }