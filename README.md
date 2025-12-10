# funasr-fastapi

基于 FastAPI 与 FunASR 的轻量语音识别服务，提供文件上传推理接口，可通过 Docker 一键部署，支持自定义模型、日志级别和运行设备配置。

## 目录结构
- `src/main.py`：FastAPI 入口，注册路由和 CORS。
- `src/core/`：配置加载、日志、音频校验与解析、启动生命周期。
- `src/routes/asr.py`：ASR 推理接口。
- `src/routes/health.py`：健康检查。
- `src/service/asr_service.py`：FunASR 推理实现。
- `download_model.py`：从 ModelScope 下载模型到本地。
- `docker-compose.yml`、`Dockerfile`：容器化配置。
- `models/`：本地模型存放目录（默认示例为 SenseVoiceSmall）。

## 前置要求
- Python 3.11+
- uv（推荐）或 pip/virtualenv
- 本地已准备好 FunASR 模型目录，或使用下方脚本下载

## 快速开始（本地）
1. 安装依赖：`uv sync`
2. 复制模型到本地或下载：
   ```bash
   uv run python download_model.py \
     -mid iic/SenseVoiceSmall \
     -ld ./models/SenseVoiceSmall
   ```
3. 创建 `.env`（示例）：
   ```
   MODEL_DIR=./models/SenseVoiceSmall
   DEVICE=cpu            # 可设 cuda / mps
   LOG_LEVEL=INFO        # TRACE/DEBUG/INFO/WARNING/ERROR
   ```
4. 启动服务：`uv run uvicorn src.main:app --host 0.0.0.0 --port 8000`

## Docker 运行
```bash
docker compose up -d
# 默认通过 8000 端口暴露
# 环境变量可在 docker-compose.yml 中调整：MODEL_DIR / DEVICE / LOG_LEVEL
```

## API
- 健康检查：`GET /health/`
- 语音识别：`POST /v1/asr/recognize`
  - 请求：`multipart/form-data`
    - `file`：音频文件（仅单声道，默认支持 `.wav` / `.mp3`）
    - `language`（可选）：`auto` | `zh` | `en` ...
    - `use_itn`（可选）：`true/false`（是否启用 ITN）
    - `other_params`（可选）：JSON 字符串，透传给 `AutoModel.generate`（如 `{"batch_size_s":30}`）
  - 示例：
    ```bash
    curl -X POST http://localhost:8000/v1/asr/recognize \
      -F "file=@/path/to/audio.wav" \
      -F "language=auto" \
      -F "use_itn=true" \
      -F 'other_params={"cache":{}}'
    ```
  - 响应：纯文本转写结果（经过 `rich_transcription_postprocess` 处理）

## 关键行为
- 启动时自动加载模型（`lifespan` 钩子，单例缓存）。
- 音频校验：文件缺失/格式不符/多声道/空数据会返回 400。
- 日志：通过 Loguru 输出 JSON，便于容器日志收集。
- 测试：`uv run pytest`（需要设置 `MODEL_DIR` 环境变量，见 `tests/core/test_config.py`）。

## 开发提示
- 调整运行设备：`.env` 或环境变量 `DEVICE=cpu|cuda|mps`。
- 若需下载其他模型：`uv run python download_model.py -mid <model_id> -ld ./models/<name>`。
- WebSocket 路由已预留在 `/v1/ws`，可按需扩展。
