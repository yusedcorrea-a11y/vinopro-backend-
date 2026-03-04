from fastapi import FastAPI, Form
import time
from llama_cpp import Llama

app = FastAPI(title="VINO PRO - Phi-2 Prueba")

MODEL_PATH = "models/phi-2-q4_K_M.gguf"

@app.on_event("startup")
async def startup_event():
    global llm
    try:
        print("🍷 Cargando Phi-2 para prueba de encoding...")
        start = time.time()
        
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,
            n_threads=8,
            n_batch=128,
            verbose=False
        )
        print(f"✅ Phi-2 cargado en {time.time()-start:.2f}s")
    except Exception as e:
        print(f"❌ Error: {e}")

@app.post("/test_encoding")
async def test_encoding(text: str = Form("Rioja con cordero")):
    """Endpoint específico para probar encoding de Phi-2"""
    if not llm:
        return {"error": "Modelo no cargado"}
    
    start = time.time()
    
    # Prompt simple
    prompt = f"Describe el vino de {text} en español:"
    
    response = llm(
        prompt,
        max_tokens=80,
        temperature=0.3,
        top_p=0.8
    )
    
    generated = response["choices"][0]["text"].strip()
    elapsed = time.time() - start
    
    # Analizar encoding
    caracteres_espanol = sum(1 for c in generated if c in 'áéíóúñüÁÉÍÓÚÑÜ')
    
    return {
        "respuesta": generated,
        "tiempo_segundos": round(elapsed, 2),
        "caracteres_español": caracteres_espanol,
        "muestra_100chars": generated[:100],
        "tiene_tildes": caracteres_espanol > 0,
        "modelo": "Phi-2 2.7B"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)  # Puerto nuevo
