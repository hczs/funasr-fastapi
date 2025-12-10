from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent


class Setting(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.joinpath(".env"),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )
    log_level: str = "INFO"
    model_dir: str = ""
    device: str = "cpu"


settings = Setting()
