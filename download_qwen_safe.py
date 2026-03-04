# download_qwen_safe.py
# Descarga SEGURA de Qwen 2.5 - NO borra nada existente

import requests
import os
from tqdm import tqdm

def download_qwen():
    print("🚀 Iniciando descarga SEGURA de Qwen 2.5 1.5B...")
    
    # URL oficial de Hugging Face (mirror)
    url = "https://hf-mirror.com/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_K_M.gguf"
    
    # Ruta de destino (models/ con nombre diferente)
    os.makedirs("models", exist_ok=True)
    destino = "models/qwen2.5-1.5b-instruct-q4_K_M.gguf"
    
    # Si YA existe, preguntar
    if os.path.exists(destino):
        print(f"⚠️  El archivo YA existe: {destino}")
        print("   Tamaño:", os.path.getsize(destino) / (1024*1024*1024), "GB")
        respuesta = input("   ¿Continuar y sobrescribir? (s/N): ")
        if respuesta.lower() != 's':
            print("❌ Descarga cancelada por el usuario")
            return
    
    # Descarga con progreso
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destino, 'wb') as file, tqdm(
            desc="Descargando",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
        
        print(f"✅ Descarga COMPLETADA: {destino}")
        print(f"📏 Tamaño: {os.path.getsize(destino) / (1024*1024*1024):.2f} GB")
        
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        # Si hay error, NO borrar archivo parcial
        if os.path.exists(destino):
            print(f"💾 Archivo parcial guardado: {destino}")

if __name__ == "__main__":
    download_qwen()
