#!/usr/bin/env bash
# WSL (Ubuntu) 一键部署脚本：安装依赖、创建虚拟环境、启动服务。
# 用法：在 WSL 内进入项目根目录后执行  bash deploy/wsl-setup.sh
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> 安装系统依赖（python3 / venv / pip）"
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip

echo "==> 创建虚拟环境"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> 安装 Python 依赖"
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> 已生成 .env，请编辑并填入 DEEPSEEK_API_KEY 后重新运行本脚本"
  exit 0
fi

echo "==> 重建知识库索引"
python scripts/ingest.py

echo "==> 启动服务（http://localhost:8000）"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
