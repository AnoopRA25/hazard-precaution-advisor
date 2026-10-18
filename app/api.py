
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.graph import graph

app = FastAPI(
    title="Hazard Precaution Advisor",
    description="Image-based hazard detection and safety advice",
    version="0.1.0",
)

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


@app.get("/")
def home():
    return {
        "project": "Hazard Precaution Advisor",
        "status": "running",
        "documentation": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    person_type: str = Form("adult"),
    language: str = Form("English"),
):
    if person_type not in {"baby", "child", "elderly", "adult"}:
        raise HTTPException(
            status_code=400,
            detail="person_type must be baby, child, elderly, or adult.",
        )

    if language not in {"English", "Kannada", "Hindi"}:
        raise HTTPException(
            status_code=400,
            detail="language must be English, Kannada, or Hindi.",
        )

    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Upload a JPEG, PNG, or WebP image.",
        )

    temp_path = None

    try:
        contents = await image.read(MAX_IMAGE_SIZE + 1)

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="The uploaded image is empty.",
            )

        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Image must be 10 MB or smaller.",
            )

        suffix = Path(image.filename or "").suffix.lower()

        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(
                status_code=400,
                detail="Use a .jpg, .jpeg, .png, or .webp filename.",
            )

        try:
            with Image.open(BytesIO(contents)) as uploaded_image:
                if uploaded_image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise HTTPException(
                        status_code=415,
                        detail="Unsupported image format.",
                    )
                uploaded_image.verify()
        except (UnidentifiedImageError, OSError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid image.",
            )

        with NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        result = graph.invoke(
            {
                "image_path": temp_path,
                "person_type": person_type,
                "language": language,
                "retry_count": 0,
            }
        )

        return {
            "setting": result.get("setting", "unknown"),
            "person_type": person_type,
            "language": language,
            "hazards": result.get("hazards", []),
            "confidence": result.get("confidence"),
            "risk_level": result.get("risk_level", "medium"),
            "predicted_risk": result.get("predicted_risk", ""),
            "reason": result.get("reason", ""),
            "precautions": result.get("precautions", []),
            "guideline_sources": result.get("guideline_sources", []),
            "message": result.get("message", ""),
            "error": result.get("error", ""),
        }

    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)
        await image.close()
