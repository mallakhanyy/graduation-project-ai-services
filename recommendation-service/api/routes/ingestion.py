from fastapi import APIRouter, Request

router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"],
)


@router.post("/all")
async def ingest_all(request: Request):

    service = request.app.state.container.document_ingestion_service

    await service.ingest_all()

    return {
        "status": "completed",
        "message": "Document ingestion finished.",
    }