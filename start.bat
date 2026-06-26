@echo off
REM Start script for Windows
IF EXIST venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Installing requirements (if missing)...
python -m pip install -r requirements.txt

echo Starting Streamlit app...
python -m streamlit run main.py

pause
