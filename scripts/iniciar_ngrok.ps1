# scripts/iniciar_ngrok.ps1
# Comprueba que el backend está en 8001, inicia ngrok, obtiene la URL pública,
# la guarda en URL_ACCESO.txt y ENLACE_PARA_MEDELLIN.txt y la copia al portapapeles.
# Uso: .\scripts\iniciar_ngrok.ps1 (desde backend_optimized)

$ErrorActionPreference = "Stop"
$BackendUrl = "http://127.0.0.1:8001"
$NgrokApi = "http://127.0.0.1:4040/api/tunnels"

# Rutas: script está en backend_optimized\scripts
$BackendRoot = Split-Path $PSScriptRoot -Parent
try { $ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path } catch { $ProjectRoot = "C:\Users\yused\Documents\VINO_PRO_FINAL" }
if (-not (Test-Path $ProjectRoot)) { $ProjectRoot = "C:\Users\yused\Documents\VINO_PRO_FINAL" }
$NgrokDir = Join-Path $ProjectRoot "ngrok"
$NgrokExe = Join-Path $NgrokDir "ngrok.exe"
$UrlAccesoFile = Join-Path $BackendRoot "URL_ACCESO.txt"
$EnlaceMedellinFile = Join-Path $BackendRoot "ENLACE_PARA_MEDELLIN.txt"

# ----- 1. Verificar que el backend está corriendo -----
Write-Host "Comprobando backend en $BackendUrl ..." -ForegroundColor Cyan
try {
    $null = Invoke-WebRequest -Uri $BackendUrl -UseBasicParsing -TimeoutSec 3
} catch {
    Write-Host "ERROR: El backend no responde en $BackendUrl" -ForegroundColor Red
    Write-Host "Inicia primero la app con: python main.py" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK - Backend activo." -ForegroundColor Green

# ----- 2. Localizar ngrok -----
if (-not (Test-Path $NgrokExe)) {
    $env:Path = "$NgrokDir;$env:Path"
    $ngrokInPath = Get-Command ngrok -ErrorAction SilentlyContinue
    if (-not $ngrokInPath) {
        Write-Host "ERROR: ngrok no encontrado. Ejecuta antes: .\scripts\instalar_ngrok.ps1" -ForegroundColor Red
        exit 1
    }
    $NgrokExe = $ngrokInPath.Source
} else {
    $env:Path = "$NgrokDir;$env:Path"
}

# ----- 3. Cerrar ngrok previo si existe (puerto 4040) -----
try {
    $null = Invoke-WebRequest -Uri $NgrokApi -UseBasicParsing -TimeoutSec 1
    Write-Host "Cerrando sesión anterior de ngrok ..." -ForegroundColor Yellow
    Get-Process -Name ngrok -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
} catch { }

# ----- 4. Iniciar ngrok en segundo plano -----
Write-Host "Iniciando ngrok (túnel a puerto 8001) ..." -ForegroundColor Cyan
$p = Start-Process -FilePath $NgrokExe -ArgumentList "http","8001" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 4

# ----- 5. Obtener URL pública desde la API de ngrok -----
$publicUrl = $null
try {
    $json = Invoke-RestMethod -Uri $NgrokApi -TimeoutSec 5
    $publicUrl = $json.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1 -ExpandProperty public_url
    if (-not $publicUrl) { $publicUrl = $json.tunnels[0].public_url }
} catch {
    Write-Host "ERROR: No se pudo obtener la URL de ngrok. ¿Tienes configurado el authtoken? (ngrok config add-authtoken ...)" -ForegroundColor Red
    if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
    exit 1
}

if (-not $publicUrl) {
    Write-Host "ERROR: No se encontró URL pública en la respuesta de ngrok." -ForegroundColor Red
    if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
    exit 1
}

# ----- 6. Guardar en archivos -----
Set-Content -Path $UrlAccesoFile -Value $publicUrl -Encoding UTF8
$textoMedellin = @"
$publicUrl

Abre este enlace en el navegador de tu móvil o PC para usar Vino Pro IA.
Puede tardar unos segundos en cargar la primera vez.
"@
Set-Content -Path $EnlaceMedellinFile -Value $textoMedellin -Encoding UTF8

# ----- 7. Copiar al portapapeles -----
Set-Clipboard -Value $publicUrl

# ----- 8. Mostrar resultado -----
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  URL pública (copiada al portapapeles):" -ForegroundColor Green
Write-Host "  $publicUrl" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
Write-Host "Guardada en: $UrlAccesoFile" -ForegroundColor Gray
Write-Host "Instrucciones para Medellín: $EnlaceMedellinFile" -ForegroundColor Gray
Write-Host ""
Write-Host "Comparte el enlace por WhatsApp. No cierres esta ventana ni apagues ngrok." -ForegroundColor Yellow
Write-Host "Para detener ngrok: Get-Process ngrok | Stop-Process" -ForegroundColor Gray
Write-Host ""
