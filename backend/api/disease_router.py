from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from services import disease_service

router = APIRouter(tags=["disease"])

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class DiagnoseTextRequest(BaseModel):
    crop: str
    symptoms: str


class DiagnoseResponse(BaseModel):
    disease_name: str
    description: str
    management_steps: list[str]
    sources: list[str] = []


@router.post("/diagnose/text", response_model=DiagnoseResponse)
async def diagnose_text(request: DiagnoseTextRequest):
    """Diagnose a crop disease from a text symptom description."""
    if not request.crop.strip() or not request.symptoms.strip():
        raise HTTPException(status_code=422, detail="Both 'crop' and 'symptoms' are required.")
    result = disease_service.diagnose_from_text(
        crop=request.crop.strip(),
        symptoms=request.symptoms.strip(),
    )
    return DiagnoseResponse(**result)


@router.post("/diagnose/image", response_model=DiagnoseResponse)
async def diagnose_image(
    crop: str = Form(default="unknown crop"),
    image: UploadFile = File(...),
):
    """Diagnose a crop disease from an uploaded leaf or plant image."""
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{image.content_type}'. Upload a JPEG, PNG, or WebP image.",
        )

    image_bytes = await image.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="Image exceeds the 5 MB size limit.")

    result = disease_service.diagnose_from_image(
        image_bytes=image_bytes,
        crop=crop.strip() or "unknown crop",
    )
    return DiagnoseResponse(**result)
