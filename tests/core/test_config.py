from src.core.config import settings


def test_get_settings() -> None:
    assert settings.model_dir != ""
