@echo off
echo === Refiny Build Script ===
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python is installed.
    pause
    exit /b 1
)

echo.
echo [2/3] Generating icons...
python scripts\generate_icon.py
if errorlevel 1 (
    echo ERROR: Icon generation failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Building Refiny.exe...
pyinstaller build\Refiny.spec --distpath dist --workpath build\work --clean
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo === Build complete! ===
echo Your app is at:  dist\Refiny.exe
echo Double-click it to launch. No Python needed.
echo.
pause
