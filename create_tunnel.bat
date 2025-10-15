@echo off
echo ========================================
echo Creating Public Tunnel for SmartCart
echo ========================================
echo.
echo Instructions:
echo 1. Keep the main server window running
echo 2. This window will create a public tunnel
echo 3. Share the public URL with your friend
echo.
echo Press any key to start the tunnel...
pause
echo.
echo Starting tunnel... (You may see a security warning - type "yes" and press Enter)
echo.
ssh -R 80:localhost:8000 serveo.net
echo.
echo Tunnel session ended.
pause