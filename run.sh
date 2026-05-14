#!/bin/bash

echo "Starting AI Code Generator..."

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
pip install -r requirements.txt

# Start FastAPI backend in background
echo "Starting FastAPI backend..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# Wait a moment for backend to start
sleep 3

# Start Streamlit UI
echo "Starting Streamlit UI..."
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0