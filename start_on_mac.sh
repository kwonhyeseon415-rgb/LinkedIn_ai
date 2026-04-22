#!/bin/bash
set -e
WEB_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$WEB_ROOT"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip

python -m pip install -r requirements.txt

if [ -f "../linkedin-skill/setup.py" ]; then
  python -m pip install -e ../linkedin-skill
fi

python -m streamlit run app.py
