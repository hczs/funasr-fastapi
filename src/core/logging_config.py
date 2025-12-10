import logging
import sys

from loguru import logger

from src.core.config import settings


class InterceptHandler(logging.Handler):
    """
    拦截 Python 标准库 logging 的日志，转发给 Loguru
    """

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.remove()

    logger.add(
        sys.stdout,  # 日志直接打印控制台，方便 Docker 收集日志
        enqueue=True,  # 非阻塞
        backtrace=True,  # 追踪异常堆栈
        diagnose=True,  # 报错的时候显示变量值
        serialize=True,  # 日志序列化为json，方便ELK 收集
        level=settings.log_level,
    )

    for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        _logger = logging.getLogger(name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False
