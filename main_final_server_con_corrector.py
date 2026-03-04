from fastapi import FastAPI, Form
import logging
import time
from llama_cpp import Llama

# Importar nuestro corrector inteligente
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from corrector_espanol import CorrectorEspanol

# Configuración de logging
logging.basicConfig(
    filename="vino_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI(title="VINO PRO - TinyLlama 1.1B + Corrector Español")

MODEL_PATH = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
llm = None
corrector = CorrectorEspanol()  # Instancia del corrector

@app.on_event("startup")
async def startup_event():
    global llm
    try:
        print("🍷 Cargando TinyLlama 1.1B con Corrector Español...")
        start = time.time()
        
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,
            n_threads=8,
            n_batch=128,
            n_gpu_layers=0,
            verbose=False
        )
        print(f"✅ Modelo cargado en {time.time()-start:.2f}s")
        print("✅ Corrector español inicializado")
    except Exception as e:
        print(f"❌ Error: {e}")

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    if not llm:
        return {"error": "Modelo no cargado"}
    
    start = time.time()
    
    # Prompt optimizado - MÁS SIMPLE para TinyLlama
    prompt = f"""Responde como sommelier experto EN ESPAÑOL.

Pregunta: {text}

Respuesta concisa:"""
    
    try:
        response = llm(
            prompt,
            max_tokens=120,      # Un poco menos para más velocidad
            temperature=0.4,     # Menos creatividad, más consistencia
            top_p=0.8,
            stop=["\n\n", "Pregunta:", "###"]
        )
        
        generated = response["choices"][0]["text"].strip()
        
        # 🎯 PASO CRÍTICO: Aplicar corrector inteligente
        generated_corregido = corrector.corregir_texto(generated)
        
        elapsed = time.time() - start
        
        # Log detallado para ver correcciones
        if generated != generated_corregido:
            logging.info(f"CORRECCIÓN: '{generated[:30]}...' -> '{generated_corregido[:30]}...'")
        
        logging.info(f"Consulta: {text} | Tiempo: {elapsed:.2f}s")
        
        return {
            "respuesta": generated_corregido,
            "respuesta_original": generated,  # Para debugging
            "tiempo_segundos": round(elapsed, 2),
            "tokens_generados": len(generated_corregido.split()),
            "correcciones_aplicadas": generated != generated_corregido,
            "modelo": "TinyLlama 1.1B + Corrector Español"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/corrector")
async def debug_corrector(texto: str = "Mxico regin caractersticas"):
    """Endpoint para probar el corrector directamente"""
    corregido = corrector.corregir_texto(texto)
    return {
        "original": texto,
        "corregido": corregido,
        "cambios": texto != corregido,
        "caracteres_español_original": sum(1 for c in texto if c in 'áéíóúñü'),
        "caracteres_español_corregido": sum(1 for c in corregido if c in 'áéíóúñü')
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)  # Puerto NUEVO para no conflictos
