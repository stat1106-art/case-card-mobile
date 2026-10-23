@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
chcp 65001 >nul
set "PY=python"
where py >nul 2>nul && set "PY=py -3"
%PY% verify_engine.py
echo.
pause
