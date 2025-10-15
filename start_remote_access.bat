@echo off
echo Starting Smart Shopping Trolley Server...
echo ========================================
echo Server will be available at:
echo - Local: http://localhost:8000
echo - Network: http://192.168.128.56:8000
echo ========================================
echo.
echo To share with friends on different networks:
echo 1. Keep this window open
echo 2. Open a NEW command prompt
echo 3. Run: ssh -R 80:localhost:8000 serveo.net
echo 4. Share the URL you get with your friends
echo.
echo Press Ctrl+C to stop the server
echo.
uvicorn main:app --host 0.0.0.0 --port 8000