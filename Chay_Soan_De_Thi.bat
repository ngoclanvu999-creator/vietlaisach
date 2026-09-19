@echo off
chcp 65001 >nul
title SOAN DE THI - Bo de chuan 2025
color 0B
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo =====================================================================
echo                        SOAN DE THI
echo   Ma tran - Ban dac ta - De ba phan - Huong dan cham
echo =====================================================================
echo.

set "PYTHON_EXE=python"
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
) else (
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo [!] Khong tim thay Python. Vui long cai Python 3.10 tro len.
        pause
        exit /b 1
    )
)

cd /d "%~dp0"
echo [*] Dang khoi dong tai: http://127.0.0.1:8502
echo [*] Khong tat cua so nay khi dang su dung phan mem.
echo.
start "" http://127.0.0.1:8502
"%PYTHON_EXE%" -m uvicorn app_de_thi.main:app --host 127.0.0.1 --port 8502
if %errorlevel% neq 0 (
    echo [!] Chuong trinh dung lai voi ma loi: %errorlevel%
)
pause
