@echo off
rem ============================================================
rem ACC 라이브 브리지 실행기 — 더블클릭으로 실행하세요.
rem 게임보다 먼저 켜도, 나중에 켜도 알아서 연결됩니다.
rem (윈도우 시작 시 자동 실행: Win+R → shell:startup →
rem  열린 폴더에 이 파일의 바로가기를 넣으세요)
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
echo 브리지가 종료되었습니다. 아무 키나 누르면 창이 닫힙니다.
pause >nul
