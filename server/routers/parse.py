from fastapi import APIRouter, File, UploadFile
from server.services.pdf_service import pdf_service

router = APIRouter(tags=["Parse"])


@router.post("/v1/parse")
@router.post("/parse")
@router.post("/v2/parse")
async def parse_document(file: UploadFile = File(...)):
    content = await file.read()
    return pdf_service.parse_pdf(content, filename=file.filename or "document.pdf")
