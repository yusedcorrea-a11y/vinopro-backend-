@echo off
echo Comprobando puerto 8001...
netstat -ano | findstr :8001
echo.
echo Probando http://127.0.0.1:8001 ...
curl -s -o nul -w "HTTP %%{http_code}\n" http://127.0.0.1:8001/ 2>nul || echo Si curl falla, abre http://127.0.0.1:8001 en el navegador
pause
