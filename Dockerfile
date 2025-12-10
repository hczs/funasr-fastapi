FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# 设置非 root 用户
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# soundfile 和 torchaudio 所需依赖
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    libgomp1 \
    libstdc++6 \
    ffmpeg \
    sox \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Install the project into `/app`
WORKDIR /app

# 复制模型
COPY ./models/SenseVoiceSmall /app/models/SenseVoiceSmall

# UV_NO_DEV 忽略 dev 依赖，仅安装必要依赖
# UV_COMPILE_BYTECODE 编译字节码，加快运行速度
# UV_LINK_MODE 指定 uv 从缓存中复制而不是软链接
# UV_TOOL_BIN_DIR 指定 uv 的工具路径
ENV UV_NO_DEV=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_TOOL_BIN_DIR=/usr/local/bin

# --mount=type=cache,target=/root/.cache/uv 构建时进行缓存，加快重复构建的速度
# --mount=type=bind,source=uv.lock,target=uv.lock把外部 uv.lock 文件绑定到容器中
# --mount=type=bind,source=pyproject.toml,target=pyproject.toml把外部 pyproject.toml 文件绑定到容器中
# 严格按照个 lock 文件来安装依赖，并且不安装项目本身
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# 添加项目源码，并且安装项目
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# 把当前虚拟环境的 bin 添加到 path 最前面，优先于镜像自带的一些可执行文件
# 确保优先使用当前虚拟环境的可执行文件，这样就不需要激活虚拟环境了
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# 使用非 root 用户启动项目，更安全
USER nonroot

# 声明容器内部服务端口
EXPOSE 8000

# 启动命令，使用 uvicorn 单进程启动
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
