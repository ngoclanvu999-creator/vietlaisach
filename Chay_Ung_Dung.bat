@echo off
chcp 65001 >nul
title BIEN SOAN SACH TOAN - VAT LY PRO
color 0B
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo =====================================================================
echo           PHAN MEM BIEN SOAN & TAI CAU TRUC SACH TOAN - VAT LY
echo =====================================================================
echo.
echo [*] Dang kiem tra moi truong Python...

set "PYTHON_EXE=python"
where python >nul 2>nul
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    ) else (
        echo [!] Khong tim thay Python! Vui long cai dat Python 3.10 tro len.
        pause
        exit /b 1
    )
)

echo [*] Dang khoi dong may chu ung dung tai: http://127.0.0.1:8501
echo [*] Trinh duyet web se tu dong mo len sau vai giay...
echo.
echo [Luu y] Khong tat cua so mau den nay khi dang su dung phan mem.
echo =====================================================================

cd /d "%~dp0"
"%PYTHON_EXE%" app.py
pause
