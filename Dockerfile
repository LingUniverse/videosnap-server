# FROM ghcr.io/starquest-ai/llm-base:pytorch-2.1.0-py3.10-cuda-11.8.0-cudnn8-devel-22.04
FROM python:3.10
LABEL maintainer="Zhou tianpeng <zhoutianpeng@ling.space>"

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
    curl git sudo wget libsndfile1 lsof && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip config set global.index-url https://pypi.org/simple

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir --ignore-installed --upgrade -r /code/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Set ENV_FILE environment variable to reference the copied file
ENV ENV_FILE=/code/videosnap-dev.env
ENV ENVIRONMENT=production

COPY ./app /code/app
COPY ./migrations /code/migrations
COPY ./videosnap-dev.env /code/videosnap-dev.env
COPY ./manifest.metadata /code/manifest.metadata
COPY ./alembic.ini /code/alembic.ini

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80", "--timeout-keep-alive", "300", "--workers", "4"]

ENV PYTHONPATH "${PYTHONPATH}:/code"

