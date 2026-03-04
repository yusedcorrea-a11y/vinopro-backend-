from fastapi import FastAPI, Form
import logging
import time
import ftfy  # <-- AÑADIDO
from llama_cpp import Llama

# Configuración de logging
logging.basicConfig(
    filename="vino_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI(title="VINO PRO - TinyLlama 1.1B")

MODEL_PATH = "models/phi-2-q4_K_M.gguf"
llm = None

@app.on_event("startup")
async def startup_event():
    global llm
    try:
        print("?? Cargando TinyLlama 1.1B...")
        start = time.time()
        
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,
            n_threads=8,
            n_batch=128,
            n_gpu_layers=0,
            verbose=False
        )
        print(f"? Modelo cargado en {time.time()-start:.2f}s")
    except Exception as e:
        print(f"? Error: {e}")

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    if not llm:
        return {"error": "Modelo no cargado"}
    
    start = time.time()
    
    # Prompt optimizado para respuestas completas
    prompt = f"""Eres un sommelier experto. Responde EN ESPAÑOL de forma clara y completa (al menos 2-3 frases).

Pregunta del cliente: {text}

Respuesta del sommelier (sé específico y profesional):"""
    
    try:
        response = llm(
            prompt,
            max_tokens=150,
            temperature=0.5,
            top_p=0.7,
            stop=["</s>"]
        )
        
        generated = response["choices"][0]["text"].strip()
        
        # CORRECCIÓN DE ENCODING MEJORADA
        # 1. Primero ftfy (arregla la mayoría)
        generated = ftfy.fix_text(generated)
        # 2. Luego corrección agresiva por si ftfy falla
        try:
            generated = generated.encode('latin-1').decode('utf-8', errors='ignore')
        except:
            pass
        # 3. Eliminar caracteres extraños persistentes
        generated = generated.replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã', 'í')
        generated = generated.replace('Ã³', 'ó').replace('Ãº', 'ú').replace('Ã±', 'ñ')
        generated = generated.replace('Ã¼', 'ü').replace('Â¿', '¿').replace('Â¡', '¡')
        
        elapsed = time.time() - start
        logging.info(f"Consulta: {text} | Tiempo: {elapsed:.2f}s | Tokens: {len(generated.split())}")
        
        return {
            "respuesta": generated,
            "tiempo_segundos": round(elapsed, 2),
            "tokens_generados": len(generated.split())
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)






