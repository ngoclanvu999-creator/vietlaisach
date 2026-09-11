@echo off
chcp 65001 >nul
title DAY TOAN BO DU AN LEN GITHUB
color 0B

echo ======================================================================
echo    CONG CU TU DONG DAY MA NGUON LEN GITHUB (ngoclanvu999-creator/vietlaisach)
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Kiem tra trang thai Git...
git status
echo.

echo [2/3] Dang day ma nguon len GitHub (main branch)...
echo Chu y: Neu trinh duyet bat len hop thoai dang nhap GitHub, ban chi can
echo bam nut 'Authorize GitCredentialManager' mau xanh la xong ngay lap tuc!
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo    >>> THANH CONG 100%%! MA NGUON DA DUOC DAY LEN GITHUB! <<<
    echo ======================================================================
    echo Link repo: https://github.com/ngoclanvu999-creator/vietlaisach
) else (
    echo.
    echo ======================================================================
    echo    >>> CO LOI XAY RA HOAC CAN DANG NHAP GITHUB TRUC TIEP <<<
    echo ======================================================================
)

echo.
echo Nhan phim bat ky de thoat...
pause >nul
