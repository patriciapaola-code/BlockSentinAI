#!/usr/bin/env bash
# Start script for Unix-like systems
set -e

if [ -f "venv/bin/activate" ]; then
  echo "Activating virtualenv..."
  source venv/bin/activate
fi

echo "Installing requirements (if missing)..."
pip install -r requirements.txt

echo "Starting Streamlit app..."
streamlit run main.py
