@echo off
chcp 65001 >nul
title TAO SHORTCUT NGOAI DESKTOP
color 0A
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

cd /d "%~dp0"

set "PYTHON_EXE=python"
where python >nul 2>nul
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    )
)

"%PYTHON_EXE%" create_shortcut.py
echo.
echo Tu nay ban chi can ra man hinh Desktop va nhap dup vao "Bien_Soan_Sach_Pro" la ung dung se tu mo!
echo.
echo Nhan phim bat ky de thoat...
pause >nul
