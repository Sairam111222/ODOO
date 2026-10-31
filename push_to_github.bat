@echo off
title SolarFlow 360 - Push to GitHub
echo ========================================================
echo  SolarFlow 360: Pushing all changes to GitHub
echo  Repository: https://github.com/Sairam111222/ODOO
echo ========================================================
echo.
cd /d "c:\Users\prane\OneDrive\Desktop\odooxecet"

echo Checking Git status...
"%LOCALAPPDATA%\Programs\MinGit\cmd\git.exe" status

echo.
echo Pushing to origin main...
echo (If prompted, log in with your GitHub account or Personal Access Token)
echo.
"%LOCALAPPDATA%\Programs\MinGit\cmd\git.exe" push origin main

echo.
if %ERRORLEVEL% equ 0 (
    echo ========================================================
    echo  SUCCESS: All changes successfully pushed to GitHub!
    echo ========================================================
) else (
    echo ========================================================
    echo  Push failed. Check your GitHub permissions/credentials.
    echo ========================================================
)
echo.
pause
