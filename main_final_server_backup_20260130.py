from fastapi import FastAPI, Form
import time
from llama_cpp import Llama

app = FastAPI(title="VINO PRO - TinyLlama 1.1B")

MODEL_PATH = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
llm = None

@app.on_event("startup")
async def startup_event():
    global llm
    try:
        print("🍷 Cargando TinyLlama 1.1B...")
        start = time.time()
        
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,           # Contexto pequeño para velocidad
            n_threads=8,         # Usa todos tus núcleos
            n_batch=128,         # Batch optimizado para CPU
            n_gpu_layers=0,      # Solo CPU
            verbose=False
        )
        print(f"✅ Modelo cargado en {time.time()-start:.2f}s")
    except Exception as e:
        print(f"❌ Error: {e}")

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    if not llm:
        return {"error": "Modelo no cargado"}
    
    start = time.time()
    
    # Prompt optimizado para TinyLlama (formato chat)
    prompt = f"""<|system|>You are a helpful wine sommelier. Answer in Spanish briefly.</s>
<|user|>Recomienda maridaje para: {text}</s>
<|assistant|>"""
    
    try:
        response = llm(
            prompt,
            max_tokens=80,        # Muy corto para velocidad
            temperature=0.5,      # Creatividad baja
            top_p=0.7,           # Sampling restringido
            stop=["</s>"] # Parar en marcadores
        )
        
        generated = response["choices"][0]["text"].strip().encode("utf-8").decode("utf-8")
        elapsed = time.time() - start
        
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




