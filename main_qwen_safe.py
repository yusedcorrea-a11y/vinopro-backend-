# main_qwen_safe.py
# Versión SEGURA para Qwen - NO modifica archivos existentes

from fastapi import FastAPI, Form
import logging
import time
import os

app = FastAPI(title="VINO PRO - Qwen 2.5 (Prueba)")

# CONFIGURACIÓN SEGURA
QWEN_PATH = "models/qwen2.5-1.5b-instruct-q4_K_M.gguf"
llm = None

# Verificar si Qwen existe
def check_qwen():
    if not os.path.exists(QWEN_PATH):
        return False, f"Archivo no encontrado: {QWEN_PATH}"
    
    file_size = os.path.getsize(QWEN_PATH) / (1024*1024*1024)  # GB
    if file_size < 0.5:  # Menos de 0.5GB probablemente incompleto
        return False, f"Archivo muy pequeño ({file_size:.2f} GB), puede estar incompleto"
    
    return True, f"Qwen disponible ({file_size:.2f} GB)"

@app.on_event("startup")
async def startup_event():
    global llm
    try:
        # Verificar primero
        disponible, mensaje = check_qwen()
        
        if not disponible:
            print(f"⚠️  {mensaje}")
            print("💡 Ejecuta: python download_qwen_safe.py")
            return
        
        print(f"🍷 {mensaje}")
        print("⏳ Cargando Qwen 2.5...")
        
        # Importar DESPUÉS de verificar (ahorra memoria si falla)
        from llama_cpp import Llama
        
        start = time.time()
        llm = Llama(
            model_path=QWEN_PATH,
            n_ctx=1024,
            n_threads=8,
            n_batch=256,
            verbose=False
        )
        print(f"✅ Qwen cargado en {time.time()-start:.2f}s")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Posibles soluciones:")
        print("   1. Asegúrate de que el archivo esté completo")
        print("   2. Verifica que llama-cpp-python esté instalado")
        print("   3. Prueba con: pip install llama-cpp-python --upgrade")

@app.get("/status")
async def status():
    disponible, mensaje = check_qwen()
    return {
        "modelo": "Qwen 2.5 1.5B",
        "disponible": disponible,
        "mensaje": mensaje,
        "archivo": QWEN_PATH,
        "alternativas": [
            "TinyLlama (actual): models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "Phi-2 (largo): models/phi-2-q4_K_M.gguf"
        ]
    }

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    if not llm:
        disponible, mensaje = check_qwen()
        return {
            "error": "Modelo no cargado",
            "solucion": mensaje,
            "comando": "python download_qwen_safe.py",
            "usar_tinylama": "http://localhost:8001/analyze/text (si está corriendo)"
        }
    
    start = time.time()
    
    try:
        # Prompt para Qwen
        prompt = f"""<|im_start|>system
Eres un experto en vinos. Responde en español claro y profesional.<|im_end|>
<|im_start|>user
Recomendación para: {text}<|im_end|>
<|im_start|>assistant
"""
        
        response = llm(
            prompt,
            max_tokens=150,
            temperature=0.7,
            top_p=0.9,
            stop=["<|im_end|>"]
        )
        
        generated = response["choices"][0]["text"].strip()
        elapsed = time.time() - start
        
        return {
            "respuesta": generated,
            "tiempo_segundos": round(elapsed, 2),
            "tokens": len(generated.split()),
            "modelo": "Qwen 2.5 1.5B",
            "encoding_check": "ESPAÑOL_CORRECTO" if any(c in generated for c in "áéíóúñ") else "POSIBLE_ERROR"
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🌐 Servidor Qwen SEGURO iniciando...")
    print("📊 Endpoint /status para verificar modelo")
    print("🔄 Si Qwen falla, TinyLlama sigue en puerto 8000")
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Puerto DIFERENTE
