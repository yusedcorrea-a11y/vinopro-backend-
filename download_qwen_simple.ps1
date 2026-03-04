# download_qwen_simple.ps1
# Descarga con PowerShell nativo - MÁS SEGURO

Write-Host "🚀 Iniciando descarga SEGURA de Qwen 2.5" -ForegroundColor Cyan
Write-Host "────────────────────────────────────────" -ForegroundColor Gray

$url = "https://hf-mirror.com/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_K_M.gguf"
$destino = "models\qwen2.5-1.5b-instruct-q4_K_M.gguf"

# Crear carpeta si no existe
if (-not (Test-Path "models")) {
    New-Item -ItemType Directory -Name "models" | Out-Null
    Write-Host "📁 Carpeta 'models' creada" -ForegroundColor Green
}

# Verificar si YA existe
if (Test-Path $destino) {
    $tamano = [math]::Round((Get-Item $destino).Length / 1GB, 2)
    Write-Host "⚠️  El archivo YA existe:" -ForegroundColor Yellow
    Write-Host "   Ruta: $destino" -ForegroundColor Gray
    Write-Host "   Tamaño: $tamano GB" -ForegroundColor Gray
    
    $respuesta = Read-Host "   ¿Continuar y sobrescribir? (s/N)"
    if ($respuesta -ne 's') {
        Write-Host "❌ Descarga cancelada por el usuario" -ForegroundColor Red
        exit 1
    }
}

Write-Host "📥 Descargando desde: $url" -ForegroundColor Cyan
Write-Host "💾 Guardando en: $destino" -ForegroundColor Cyan
Write-Host "⏳ Esto puede tardar varios minutos..." -ForegroundColor Yellow

try {
    # Usar Invoke-WebRequest con progreso
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $url -OutFile $destino
    
    # Verificar descarga
    if (Test-Path $destino) {
        $tamanoFinal = [math]::Round((Get-Item $destino).Length / 1GB, 2)
        Write-Host "`n✅ Descarga COMPLETADA" -ForegroundColor Green
        Write-Host "   Tamaño: $tamanoFinal GB" -ForegroundColor Green
        Write-Host "   Ruta: $destino" -ForegroundColor Gray
        
        # Verificar tamaño mínimo (debería ser ~1.5GB)
        if ($tamanoFinal -gt 1) {
            Write-Host "🎯 Archivo de tamaño CORRECTO" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Archivo más pequeño de lo esperado" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Error: Archivo no se creó" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error en descarga: $_" -ForegroundColor Red
    
    # Si hay archivo parcial, informar pero NO borrar
    if (Test-Path $destino) {
        $tamanoParcial = [math]::Round((Get-Item $destino).Length / 1MB, 1)
        Write-Host "💾 Archivo parcial guardado: $tamanoParcial MB" -ForegroundColor Yellow
        Write-Host "   Puedes reanudar manualmente más tarde" -ForegroundColor Gray
    }
}

Write-Host "`n🔧 Pasos siguientes:" -ForegroundColor Cyan
Write-Host "   1. Iniciar servidor Qwen: python main_qwen_safe.py" -ForegroundColor Gray
Write-Host "   2. Verificar: curl http://localhost:8002/status" -ForegroundColor Gray
Write-Host "   3. Probar: curl -X POST http://localhost:8002/analyze/text -d 'text=Malbec'" -ForegroundColor Gray
