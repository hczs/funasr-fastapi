from contextlib import asynccontextmanager

from loguru import logger

from src.routes.deps import get_asr_service_singleton


@asynccontextmanager
async def lifespan(app):  # noqa: ARG001
    logger.info("ASR Server Starting...")
    # load asr model and service
    get_asr_service_singleton()
    logger.info("ASR Server Start Completed!")
    yield
