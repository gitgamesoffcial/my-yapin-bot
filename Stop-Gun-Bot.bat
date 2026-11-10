@echo off
echo Stopping Start-Gun-Bot...
taskkill /FI "WINDOWTITLE eq Start-Gun-Bot*" /F /T
taskkill /IM python.exe /F
echo.
echo Start-Gun-Bot has been shut down successfully.
pause
