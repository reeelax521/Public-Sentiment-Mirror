#!/usr/bin/env bash
set -euo pipefail

cd /opt/public-sentiment-mirror

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

streamlit run app.py \
  --server.address 127.0.0.1 \
  --server.port 8501 \
  --server.headless true

