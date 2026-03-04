Write-Host "🍷 VINO PRO - ESTADO INSTANTÁNEO" -ForegroundColor Cyan
Write-Host "────────────────────────────────"
python -c "
import sys
try:
    with open('main_final_server.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f'📄 Servidor: {len(lines)} líneas')
    
    import subprocess
    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
    if ':8000' in result.stdout:
        print('🟢 Puerto 8000: ACTIVO')
    else:
        print('🔴 Puerto 8000: INACTIVO')
        
except Exception as e:
    print(f'❌ Error: {e}')
"
