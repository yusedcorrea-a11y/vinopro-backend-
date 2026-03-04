@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ============================================
echo   VinoPro - Instalador Agente Local (8080)
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Instale Python 3.10 o superior y anadalo al PATH del sistema.
    echo.
    pause
    exit /b 1
)

echo [1/6] Python encontrado.
python --version

REM Crear entorno virtual venv_agent
echo.
echo [2/6] Entorno virtual venv_agent...
if not exist "venv_agent" (
    python -m venv venv_agent
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] No se pudo crear venv_agent.
        pause
        exit /b 1
    )
    echo       Creado venv_agent.
) else (
    echo       Ya existe venv_agent.
)

REM Activar entorno e instalar dependencias
echo.
echo [3/6] Activando venv e instalando dependencias...
call venv_agent\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se pudo activar venv_agent.
    pause
    exit /b 1
)

pip install -q fastapi uvicorn httpx pydantic python-dotenv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al instalar paquetes.
    pause
    exit /b 1
)
echo       fastapi, uvicorn, httpx, pydantic, python-dotenv instalados.

REM Carpeta agente_local
echo.
echo [4/6] Carpeta agente_local...
if not exist "agente_local" (
    echo [ERROR] No existe la carpeta agente_local. Debe estar junto a este script.
    pause
    exit /b 1
)
echo       OK.

REM OPENROUTER_API_KEY opcional
echo.
echo [5/6] API Key de OpenRouter (opcional, para IA generativa gratuita)...
if "%OPENROUTER_API_KEY%"=="" (
    set INPUT_KEY=
    set /p INPUT_KEY="Pegue su clave o pulse Enter para omitir: "
    if not "!INPUT_KEY!"=="" set OPENROUTER_API_KEY=!INPUT_KEY!
    if "!OPENROUTER_API_KEY!"=="" (
        echo       Sin clave. El agente usara respuestas rule-based.
    ) else (
        echo       Clave configurada para esta sesion.
    )
) else (
    echo       OPENROUTER_API_KEY ya estaba definida.
)

REM Resumen
echo.
echo [6/6] Configuracion lista.
echo.
echo   Backend VinoPro debe estar en: http://127.0.0.1:8001
echo   Agente se ejecutara en:         http://127.0.0.1:8080
echo.
echo   Para arrancar el agente manualmente:
echo     cd %~dp0
echo     venv_agent\Scripts\activate
echo     set AGENTE_PORT=8080
echo     set VINOPRO_BACKEND_URL=http://127.0.0.1:8001
echo     python -m agente_local.server
echo.

set /p ARRANCAR="Desea arrancar el agente ahora? (S/N): "
if /i "%ARRANCAR%"=="S" (
    set AGENTE_PORT=8080
    set VINOPRO_BACKEND_URL=http://127.0.0.1:8001
    echo.
    echo Iniciando agente en http://127.0.0.1:8080
    echo Para detener: Ctrl+C
    echo ============================================
    python -m agente_local.server
    pause
) else (
    echo.
    echo Para arrancar mas tarde, ejecute este mismo script de nuevo y elija S.
    echo O use los comandos manuales del bloque [6/6] anterior.
    echo.
    pause
)
