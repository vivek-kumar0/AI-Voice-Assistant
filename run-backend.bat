@echo off
cd /d "%~dp0backend"
if not exist venv python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
if not exist .env copy .env.example .env
echo.
echo Edit backend\.env and set OPENAI_API_KEY to your real key before using Nova AI.
echo.
uvicorn app.main:app --reload --port 8000
