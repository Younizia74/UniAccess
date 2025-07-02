@echo off
REM Active l'environnement virtuel et lance le projet NVDA-Linux
cd /d %~dp0
if not exist venv (
    echo Creation de l'environnement virtuel...
    python -m venv venv
)
call venv\Scripts\activate.bat
if exist requirements_windows.txt (
    pip install -r requirements_windows.txt
) else (
    pip install -r requirements.txt
)
cd src
python main.py
cd ..
pause 