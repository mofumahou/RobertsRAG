from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health")
def health_check() -> dict[str, str]:
    return JSONResponse(
        content={"status": "ok"},
        status_code=status.HTTP_200_OK,
    )