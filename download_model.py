from argparse import ArgumentParser
from pathlib import Path

from loguru import logger
from modelscope import snapshot_download


def parse_args() -> tuple[str, Path]:
    parser = ArgumentParser(
        description="Download a ModelScope model into the local models directory."
    )
    parser.add_argument(
        "-mid",
        "--model_id",
        required=True,
        help="ModelScope model id, e.g. iic/punc_ct-transformer_cn-en-common-vocab471067-large",
    )
    parser.add_argument(
        "-ld",
        "--local_dir",
        type=Path,
        help="Target download directory (default: ./models/<model_name>)",
    )
    args = parser.parse_args()
    model_root = Path(__file__).resolve().parent / "models"
    local_dir = args.local_dir or model_root / args.model_id.split("/")[-1]
    return args.model_id, local_dir


def main() -> None:
    model_id, local_dir = parse_args()
    local_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"开始下载模型: {model_id} -> {local_dir}")
    output_dir = snapshot_download(model_id=model_id, local_dir=str(local_dir))
    logger.info(f"模型文件已下载到: {output_dir}")


if __name__ == "__main__":
    # example
    # uv run ./download_model.py \
    #  -mid iic/punc_ct-transformer_cn-en-common-vocab471067-large \
    #  -ld ./models/punc_ct-transformer-large
    main()
