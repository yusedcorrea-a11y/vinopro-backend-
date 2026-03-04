# deploy.ps1 - Despliegue de Vino Pro IA (Windows / servidor remoto)
# Uso: .\deploy.ps1 [-TargetDir "C:\ruta\destino"] [-Restart]
# Opcional: $env:DEPLOY_TARGET = "usuario@servidor:/var/www/vino-pro"

param(
    [string]$TargetDir = $env:DEPLOY_TARGET,
    [switch]$Restart
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

if (-not $TargetDir) {
    Write-Host "Uso: .\deploy.ps1 -TargetDir 'C:\ruta\app'"
    Write-Host "  o: `$env:DEPLOY_TARGET = 'C:\ruta'; .\deploy.ps1"
    exit 1
}

Write-Host "Proyecto: $ProjectRoot -> Destino: $TargetDir"

# Carpetas y archivos a copiar (excluir venv, __pycache__, .env con datos sensibles)
$exclude = @("venv", "venv_*", "__pycache__", "*.pyc", ".git", ".env")
$include = @("*.py", "templates", "static", "data", "services", "routes", "requirements_produccion.txt", ".env.example")

if (Test-Path $TargetDir) {
    Write-Host "Copiando archivos..."
    Copy-Item -Path "$ProjectRoot\app.py" -Destination $TargetDir -Force
    Copy-Item -Path "$ProjectRoot\requirements_produccion.txt" -Destination $TargetDir -Force
    Copy-Item -Path "$ProjectRoot\templates" -Destination $TargetDir -Recurse -Force
    Copy-Item -Path "$ProjectRoot\static" -Destination $TargetDir -Recurse -Force
    Copy-Item -Path "$ProjectRoot\data" -Destination $TargetDir -Recurse -Force
    Copy-Item -Path "$ProjectRoot\services" -Destination $TargetDir -Recurse -Force
    Copy-Item -Path "$ProjectRoot\routes" -Destination $TargetDir -Recurse -Force
    if (Test-Path "$ProjectRoot\.env") { Copy-Item "$ProjectRoot\.env" "$TargetDir\.env" -Force }
    Copy-Item "$ProjectRoot\.env.example" "$TargetDir\.env.example" -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "Creando $TargetDir y copiando proyecto..."
    New-Item -ItemType Directory -Path $TargetDir -Force
    Copy-Item -Path "$ProjectRoot\*" -Destination $TargetDir -Recurse -Force -Exclude "venv","venv_*",".git"
}

Write-Host "Instalando dependencias en destino..."
Push-Location $TargetDir
try {
    if (Get-Command pip -ErrorAction SilentlyContinue) {
        pip install -r requirements_produccion.txt --quiet
    } else {
        & "$ProjectRoot\venv\Scripts\pip.exe" install -r requirements_produccion.txt --quiet
    }
} finally {
    Pop-Location
}

Write-Host "Variables de entorno: crear/editar .env en destino con:"
Write-Host "  HOST=0.0.0.0"
Write-Host "  PORT=8000"
Write-Host "  CORS_ORIGINS=https://tudominio.com"
Write-Host "  STRIPE_SECRET_KEY=sk_live_xxx"
Write-Host "  STRIPE_PUBLISHABLE_KEY=pk_live_xxx"
Write-Host "  STRIPE_WEBHOOK_SECRET=whsec_xxx"
Write-Host "Despliegue listo. Para iniciar: python app.py  (o configurar servicio/PM2)"
if ($Restart) {
    Write-Host "Reiniciando no automatizado en este script; hazlo manualmente en el servidor."
}
Write-Host "OK."
