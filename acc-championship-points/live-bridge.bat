@echo off
rem ============================================================
rem ACC Live Bridge launcher - just double-click this file.
rem It is fine to start this before or after the game.
rem Auto-start on boot: Win+R -> shell:startup -> put a
rem shortcut to this file in the folder that opens.
rem (ASCII only: cmd reads .bat files in the OEM codepage,
rem  so Korean text here would break on Korean Windows.)
rem ============================================================
chcp 65001 >nul
cd /d "%~dp0"
if not exist "live-bridge.py" (
    echo [ERROR] live-bridge.py was not found in this folder:
    echo         %~dp0
    echo Put live-bridge.bat and live-bridge.py in the SAME folder,
    echo then run this file again.
    echo.
    echo Press any key to close this window.
    pause >nul
    exit /b 1
)
where python >nul 2>nul
if %errorlevel%==0 (
    python live-bridge.py %*
) else (
    py -3 live-bridge.py %*
)
echo.
echo Bridge stopped. Press any key to close this window.
pause >nul
