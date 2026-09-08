FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    zstd \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /workspace

# Pythonパッケージのインストール（必要に応じてpoetryやpip）
RUN pip install --no-cache-dir \
    numpy \
    opencv-python-headless \
    torch \
    torchvision \
    matplotlib \
    jupyter