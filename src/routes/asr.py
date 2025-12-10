from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from src.core.audio import MonoAudioLoader, RawAudio
from src.routes.deps import get_asr_service_singleton
from src.schemas.asr import ASRConfig
from src.service.asr_service import ASRService

router = APIRouter(prefix="/asr")


@router.post("/recognize")
async def asr(
    asr_service: Annotated[ASRService, Depends(get_asr_service_singleton)],
    raw_audio: Annotated[RawAudio, Depends(MonoAudioLoader())],
    config: Annotated[ASRConfig, Depends(ASRConfig.as_form)],
):
    logger.bind(
        filename=raw_audio.filename,
        sample_rate=raw_audio.sample_rate,
        duration=raw_audio.duration,
        config=config.model_dump(),
    ).info("收到语音请求，准备推理")
    return await asr_service.recognize(raw_audio, config)
