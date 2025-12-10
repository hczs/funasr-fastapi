from typing import Any

from fastapi import Form
from pydantic import BaseModel, Field, Json


class ASRConfig(BaseModel):
    language: str = Field(default="auto")
    use_itn: bool = True

    other_params: Json[dict[str, Any]] = Field(default_factory=dict)

    @classmethod
    def as_form(
        cls,
        language: str = Form("auto", description="语言"),
        use_itn: bool = Form(True, description="是否开启ITN"),
        other_params: str = Form("{}", description="其他参数 JSON 字符串"),
    ):
        return cls.model_validate(
            {"language": language, "use_itn": use_itn, "other_params": other_params}
        )
