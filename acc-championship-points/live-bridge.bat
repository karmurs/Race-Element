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
where python >nul 2>nul
if %errorlevel%==0 (
    python live-bridge.py %*
) else (
    py -3 live-bridge.py %*
)
echo.
echo Bridge stopped. Press any key to close this window.
pause >nul
