@echo off
:: Ép cmd dùng bảng mã UTF-8 để hiển thị tiếng Việt và Emoji
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

:: Chuyển hướng về thư mục chứa dự án
cd /d "D:\MyPC\MyCode\MoneyTest"

echo ===================================================
echo [*] DANG TAI DU LIEU VN30 PHIEN MOI NHAT...
echo ===================================================
py src/fetch_vn30.py

echo.
echo ===================================================
echo [*] DANG QUET TIN HIEU DONG TIEN...
echo ===================================================
py src/scanner.py

echo.
echo Hoan tat! Nhan phim bat ky de dong cua so...
pause