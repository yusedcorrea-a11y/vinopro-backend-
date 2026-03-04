# download_qwen_final.ps1
# Descarga DEFINITIVA de Qwen2.5-0.5B

$url = "https://huggingface.co/TheBloke/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct.Q4_K_M.gguf"
$destino = "models\qwen2.5-0.5b-instruct.Q4_K_M.gguf"

Write-Host "🎯 DESCARGA DEFINITIVA QWEN 2.5 0.5B" -ForegroundColor Cyan
Write-Host "────────────────────────────────────" -ForegroundColor Gray

# Verificar espacio
$drive = Get-PSDrive C
$espacioGB = [math]::Round($drive.Free / 1GB, 1)
Write-Host "Espacio libre en C: $espacioGB GB" -ForegroundColor $(if($espacioGB -gt 5){"Green"}else{"Yellow"})

if (Test-Path $destino) {
    $tamano = [math]::Round((Get-Item $destino).Length / 1GB, 2)
    Write-Host "⚠️  Archivo ya existe ($tamano GB)" -ForegroundColor Yellow
    $respuesta = Read-Host "   ¿Sobrescribir? (s/N)"
    if ($respuesta -ne 's') {
        Write-Host "⏸️  Usando archivo existente" -ForegroundColor Gray
        exit 0
    }
}

Write-Host "📥 Descargando Qwen2.5-0.5B (0.3GB)..." -ForegroundColor Green
Write-Host "   URL: $url" -ForegroundColor DarkGray
Write-Host "   Destino: $destino" -ForegroundColor DarkGray
Write-Host "   Estimación: 5-15 minutos" -ForegroundColor Yellow

try {
    # Descarga con progreso visual
    $ProgressPreference = 'SilentlyContinue'
    $startTime = Get-Date
    
    Invoke-WebRequest -Uri $url -OutFile $destino -ErrorAction Stop
    
    $endTime = Get-Date
    $duration = [math]::Round(($endTime - $startTime).TotalMinutes, 1)
    
    if (Test-Path $destino) {
        $tamanoFinal = [math]::Round((Get-Item $destino).Length / 1GB, 2)
        Write-Host "`n✅ DESCARGA COMPLETADA" -ForegroundColor Green
        Write-Host "   Tamaño: $tamanoFinal GB" -ForegroundColor Green
        Write-Host "   Tiempo: $duration minutos" -ForegroundColor Green
        Write-Host "   Ruta: $destino" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error en descarga: $_" -ForegroundColor Red
    if (Test-Path $destino) {
        $tamanoParcial = [math]::Round((Get-Item $destino).Length / 1MB, 1)
        Write-Host "💾 Archivo parcial ($tamanoParcial MB) guardado" -ForegroundColor Yellow
    }
}
