@echo off
title DS PORTFOLIO launcher
cd /d "%~dp0"
echo ============================================================
echo  DS PORTFOLIO - local launcher
echo ============================================================
echo.
where python >nul 2>nul || (echo ERROR: Python not found. Install python.org, tick "Add to PATH", retry. & pause & exit /b 1)
echo [1/3] Checking packages (installs once if missing)...
python -c "import pandas,numpy,matplotlib,openpyxl" 2>nul || python -m pip install pandas numpy matplotlib openpyxl
echo   done.
echo.
echo [2/3] Making sure files are downloaded from OneDrive (not cloud-only)...
attrib +P -U "ds-demand-cockpit\ds-demand-cockpit\out\plan\*" /s >nul 2>nul
attrib +P -U "ds-copilot\ds-copilot\db\*" /s >nul 2>nul
attrib +P -U "ds-doc-to-decision\ds-doc-to-decision\data\*" /s >nul 2>nul
echo   done.
echo.
echo [3/3] Launching three servers, each in its own window.
echo   If a window shows a red error, copy it to Raj - that window will STAY OPEN.
start "COCKPIT  :8765" cmd /k "cd /d "%~dp0ds-demand-cockpit\ds-demand-cockpit" && echo Building/serving cockpit... && python src\server.py & echo. & echo [server stopped - read any error above] & pause"
start "COPILOT  :8770" cmd /k "cd /d "%~dp0ds-copilot\ds-copilot" && echo Building copilot DB... && python src\db.py && echo Serving copilot... && python src\server.py 8770 & echo. & echo [server stopped - read any error above] & pause"
start "INVROBOT :8780" cmd /k "cd /d "%~dp0ds-doc-to-decision\ds-doc-to-decision" && echo Calibrating... && python src\calibrate.py && echo Serving invoice robot... && python src\server.py 8780 & echo. & echo [server stopped - read any error above] & pause"
echo.
echo   Waiting 30s for them to build, then opening browser tabs...
timeout /t 30 >nul
start "" "%~dp0HOME.html"
echo.
echo   If a page says "can't reach" - that server's window shows why. First run
echo   may need another 30-60s; just refresh the tab. Windows Firewall may ask to
echo   "Allow access" for Python the first time - click Allow.
echo.
pause
