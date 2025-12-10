from fastapi import APIRouter

router = APIRouter(prefix="/health")


@router.get("/")
async def health() -> str:
    return "ASR Server is running!"
