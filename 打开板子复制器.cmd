@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title 算法板子复制器

py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 (
    py -3 "tools\serve_snippet_picker.py" %*
    set "picker_exit=%errorlevel%"
    goto :finished
)

python -c "import sys" >nul 2>nul
if not errorlevel 1 (
    python "tools\serve_snippet_picker.py" %*
    set "picker_exit=%errorlevel%"
    goto :finished
)

echo 未找到 Python 3。请先安装 Python，并勾选“Add Python to PATH”。
pause
exit /b 1

:finished
if not "%picker_exit%"=="0" (
    echo.
    echo 复制器异常退出，错误码：%picker_exit%
    pause
)
exit /b %picker_exit%
