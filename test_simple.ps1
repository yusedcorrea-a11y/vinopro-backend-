Write-Host "=== PRUEBA OCR VINO PRO ===" -ForegroundColor Green

# Verificar servidor
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    Write-Host "✅ Servidor activo: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Servidor no disponible" -ForegroundColor Red
    exit
}

# Usar la imagen que ya tenemos
$imagePath = ".\viña_pedrosa.jpg"
if (-not (Test-Path $imagePath)) {
    Write-Host "❌ No se encuentra: $imagePath" -ForegroundColor Red
    exit
}

Write-Host "📸 Usando imagen: viña_pedrosa.jpg" -ForegroundColor Cyan

# Subir imagen usando curl (más fiable)
Write-Host "`n🔄 Enviando imagen al servidor..." -ForegroundColor Yellow

try {
    $result = curl.exe -X POST "http://localhost:8000/ocr" -F "file=@$imagePath" 2>$null | ConvertFrom-Json
    
    if ($result.success) {
        Write-Host "`n✅ ¡ÉXITO! Vino escaneado:" -ForegroundColor Green
        Write-Host "   Nombre: $($result.data.name)"
        Write-Host "   Productor: $($result.data.producer)"
        Write-Host "   Añada: $($result.data.vintage)"
        Write-Host "   ID: $($result.wine_id)"
        Write-Host "`n🍷 Vino guardado en tu bodega digital." -ForegroundColor Magenta
    } else {
        Write-Host "`n❌ Error en OCR:" -ForegroundColor Red
        Write-Host "   $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "`n❌ Error de conexión: $_" -ForegroundColor Red
}

Write-Host "`nPrueba completada." -ForegroundColor Gray
