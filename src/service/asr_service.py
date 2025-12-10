from functools import partial
from typing import Protocol

from fastapi.concurrency import run_in_threadpool
from funasr import AutoModel
from funasr.utils import postprocess_utils

from src.core.audio import RawAudio
from src.schemas.asr import ASRConfig


class ASRService(Protocol):
    async def recognize(self, raw_audio: RawAudio, asr_config: ASRConfig) -> str: ...


class FunASRService:
    def __init__(self, auto_model: AutoModel) -> None:
        self.model: AutoModel = auto_model

    async def recognize(self, raw_audio: RawAudio, asr_config: ASRConfig) -> str:
        res = await run_in_threadpool(
            partial(
                self.model.generate,
                input=raw_audio.samples,
                fs=raw_audio.sample_rate,
                **asr_config.model_dump(),
            )
        )
        return postprocess_utils.rich_transcription_postprocess(res[0]["text"])
