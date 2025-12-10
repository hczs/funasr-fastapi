from dataclasses import dataclass
from functools import partial
import io

from fastapi import File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
import numpy as np
import soundfile as sf


@dataclass
class RawAudio:
    samples: np.ndarray
    sample_rate: int
    filename: str

    @property
    def duration(self) -> float:
        return len(self.samples) / self.sample_rate


class MonoAudioLoader:
    def __init__(self, allowed_exts: set[str] | None = None):
        self.allowed_exts: set[str] = allowed_exts or {".wav", ".mp3"}

    async def __call__(self, file: UploadFile = File(...)) -> RawAudio:
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="请上传音频文件！"
            )
        # 校验文件类型
        filename = (file.filename or "").lower()
        if not any(filename.endswith(ext) for ext in self.allowed_exts):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型. 允许: {self.allowed_exts}",
            )

        # 读取文件
        content: bytes = await file.read()
        try:
            data, sr = await run_in_threadpool(
                partial(
                    sf.read, file=io.BytesIO(initial_bytes=content), dtype="float32"
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"音频文件损坏: {e}"
            )

        # 校验单声道
        # Soundfile 读取规则：
        # 单声道 -> shape (N,)
        # 多声道 -> shape (N, Channels)

        # 判断是否为多声道
        if data.ndim > 1 and data.shape[1] > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"仅支持单声道音频 (Mono). 当前声道数: {data.shape[1]}",
            )

        # 确保数据不是空的
        if len(data) == 0:
            raise HTTPException(status_code=400, detail="音频内容为空")

        return RawAudio(samples=data, sample_rate=sr, filename=filename)
