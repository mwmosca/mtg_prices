@echo off
REM ==== CONFIGURATION ====
set COMMIT_MSG=Automated price data commit %date% %time%
REM --------------------------------------------------------

REM Add all changes (you can fine‑tune this)
git add data\price_history.csv reports\price_report.csv
if errorlevel 1 (
    echo git add failed
    exit /b 1
)

REM Commit (skip if nothing to commit)
git diff-index --quiet HEAD --
if %errorlevel% EQU 0 (
    echo Nothing to commit – exiting
    exit /b 0
) else (
    git commit -m "%COMMIT_MSG%"
    if errorlevel 1 (
        echo git commit failed
        exit /b 1
    )
)

REM Push to the default remote (origin) and branch (usually main/master)
git push origin HEAD
if errorlevel 1 (
    echo git push failed
    exit /b 1
)

echo Success: %COMMIT_MSG%
exit /b 0
