@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title 生成算法板子文本

py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 (
    py -3 "tools\export_snippet_text.py" %*
    if errorlevel 1 pause
    exit /b %errorlevel%
)

python -c "import sys" >nul 2>nul
if not errorlevel 1 (
    python "tools\export_snippet_text.py" %*
    if errorlevel 1 pause
    exit /b %errorlevel%
)

echo 未找到 Python 3。请先安装 Python，并勾选“Add Python to PATH”。
pause
exit /b 1
