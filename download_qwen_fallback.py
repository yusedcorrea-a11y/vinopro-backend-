# download_qwen_fallback.py
# Alternativa si PowerShell falla

import os
import sys

def main():
    print("📦 Método alternativo de descarga")
    print("────────────────────────────────")
    
    destino = "models/qwen2.5-1.5b-instruct-q4_K_M.gguf"
    
    # Verificar si existe
    if os.path.exists(destino):
        tamaño = os.path.getsize(destino) / (1024**3)  # GB
        print(f"⚠️  Archivo ya existe: {tamaño:.2f} GB")
        
        respuesta = input("¿Continuar? (s/N): ").strip().lower()
        if respuesta != 's':
            print("Cancelado")
            return
    
    print("\n🔧 INSTRUCCIONES MANUALES:")
    print("1. Abre tu navegador web")
    print("2. Ve a: https://hf-mirror.com/Qwen/Qwen2.5-1.5B-Instruct-GGUF")
    print("3. Busca: 'qwen2.5-1.5b-instruct-q4_K_M.gguf'")
    print("4. Descarga manualmente (~1.5 GB)")
    print("5. Guarda en: models/qwen2.5-1.5b-instruct-q4_K_M.gguf")
    print("\n💡 O usa este comando en PowerShell:")
    print("   Invoke-WebRequest -Uri 'https://hf-mirror.com/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_K_M.gguf' -OutFile 'models/qwen2.5-1.5b-instruct-q4_K_M.gguf'")

if __name__ == "__main__":
    main()
