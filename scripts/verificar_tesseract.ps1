# scripts/verificar_tesseract.ps1
# Comprueba si Tesseract OCR está instalado y en el PATH (necesario para escanear etiquetas).
# Uso: .\scripts\verificar_tesseract.ps1

$ErrorActionPreference = "SilentlyContinue"
$cmd = Get-Command tesseract -ErrorAction SilentlyContinue
if ($cmd) {
    Write-Host "Comprobando Tesseract..." -ForegroundColor Cyan
    $version = & tesseract --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK - Tesseract instalado y en el PATH." -ForegroundColor Green
        Write-Host $version
        exit 0
    }
}
Write-Host "Tesseract no está instalado o no está en el PATH." -ForegroundColor Red
Write-Host "Instrucciones: docs/INSTALAR_TESSERACT_WINDOWS.md" -ForegroundColor Yellow
Write-Host "Descarga: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Gray
exit 1
