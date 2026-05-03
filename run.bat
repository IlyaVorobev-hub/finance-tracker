@echo off
start cmd /k ".\.venv\Scripts\Activate.ps1 && python -m uvicorn src.api.main:app --reload"
timeout /t 3
start cmd /k ".\.venv\Scripts\Activate.ps1 && streamlit run src/ui/app.py"