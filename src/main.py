from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.core.lifespan import lifespan
from src.core.logging_config import setup_logging
from src.routes import asr, health, ws

setup_logging()

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=ws.router, prefix="/v1")
app.include_router(router=asr.router, prefix="/v1")
app.include_router(router=health.router)
