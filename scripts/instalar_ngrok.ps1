# scripts/instalar_ngrok.ps1
# Descarga ngrok, lo descomprime en VINO_PRO_FINAL\ngrok y deja la ruta lista para usar.
# Ejecutar: .\scripts\instalar_ngrok.ps1 (desde backend_optimized) o con PowerShell como Administrador si hay restricciones.

$ErrorActionPreference = "Stop"
$NgrokZipUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
# Carpeta del proyecto VINO_PRO_FINAL (sube dos niveles desde scripts)
try {
    $ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
} catch {
    $ProjectRoot = "C:\Users\yused\Documents\VINO_PRO_FINAL"
}
if (-not (Test-Path $ProjectRoot)) { $ProjectRoot = "C:\Users\yused\Documents\VINO_PRO_FINAL" }
$NgrokDir = Join-Path $ProjectRoot "ngrok"
$ZipPath = Join-Path $env:TEMP "ngrok-windows-amd64.zip"

Write-Host "[1/4] Creando carpeta ngrok: $NgrokDir" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $NgrokDir | Out-Null

Write-Host "[2/4] Descargando ngrok desde ngrok.com ..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri $NgrokZipUrl -OutFile $ZipPath -UseBasicParsing
} catch {
    Write-Host "ERROR: No se pudo descargar. Comprueba internet o descarga manual desde https://ngrok.com/download" -ForegroundColor Red
    exit 1
}

Write-Host "[3/4] Descomprimiendo en $NgrokDir ..." -ForegroundColor Cyan
Expand-Archive -Path $ZipPath -DestinationPath $NgrokDir -Force

Write-Host "[4/4] Limpiando archivo temporal ..." -ForegroundColor Cyan
Remove-Item -Path $ZipPath -Force -ErrorAction SilentlyContinue

$NgrokExe = Join-Path $NgrokDir "ngrok.exe"
if (-not (Test-Path $NgrokExe)) {
    Write-Host "ERROR: No se encontró ngrok.exe en $NgrokDir" -ForegroundColor Red
    exit 1
}

# Añadir al PATH de la sesión actual (temporal)
$env:Path = "$NgrokDir;$env:Path"
Write-Host ""
Write-Host "OK - ngrok instalado en: $NgrokDir" -ForegroundColor Green
Write-Host "Para usar en esta sesión ya está en el PATH." -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANTE: Configura tu authtoken (gratis en https://ngrok.com/signup):" -ForegroundColor Yellow
Write-Host "  & '$NgrokExe' config add-authtoken TU_TOKEN" -ForegroundColor White
Write-Host ""
Write-Host "Para que el PATH sea permanente, añade esta carpeta en Variables de entorno del sistema:" -ForegroundColor Yellow
Write-Host "  $NgrokDir" -ForegroundColor White
