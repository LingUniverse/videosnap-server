#!/bin/bash
source /home/vscode/venv/bin/activate
pip install -r requirements.txt
sudo chown vscode:vscode /workspace
# pre-commit install

cd /workspace

# 运行数据库迁移
alembic upgrade head