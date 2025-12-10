from functools import lru_cache

from funasr import AutoModel
from loguru import logger

from src.core.config import settings
from src.service.asr_service import FunASRService


@lru_cache(maxsize=1)
def get_asr_service_singleton() -> FunASRService:
    def load_asr_model() -> AutoModel:
        model_path = settings.model_dir
        logger.info(f"加载模型: {model_path}")
        model = AutoModel(
            model=model_path,
            device=settings.device,
            # vad_model="../models/fsmn-vad-zh",
            # punc_model="../models/punc_ct-transformer",
            # vad_kwargs={"max_single_segment_time": 60000},
            disable_update=True,
        )
        logger.info(f"模型加载完成: {model.kwargs}")
        return model

    model: AutoModel = load_asr_model()
    service = FunASRService(auto_model=model)
    return service
