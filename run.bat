@echo off
echo Starting AI Code Generator...

REM Activate virtual environment
call .venv\Scripts\activate.bat

//REM Install dependencies if needed
//pip install -r requirements.txt

REM Start FastAPI backend in background
echo Starting FastAPI backend...
start /B uvicorn main:app --reload --host 0.0.0.0 --port 8000

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start Streamlit UI
echo Starting Streamlit UI...
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0

pause