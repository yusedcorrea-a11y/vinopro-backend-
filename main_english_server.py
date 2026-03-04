# main_english_server.py
# VINO PRO en inglés (funcional ahora) - Español después

from fastapi import FastAPI, Form
import logging
import time
from llama_cpp import Llama

app = FastAPI(title="VINO PRO - English Sommelier (Temporary)")

MODEL_PATH = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
llm = None

@app.on_event("startup")
async def startup_event():
    global llm
    try:
        print("🍷 Loading TinyLlama 1.1B (English optimized)...")
        start = time.time()
        
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,
            n_threads=8,
            n_batch=128,
            n_gpu_layers=0,
            verbose=False
        )
        print(f"✅ Model loaded in {time.time()-start:.2f}s")
        print("🌍 Ready for English wine consultations")
        print("💡 Note: Spanish support coming soon with better model")
        
    except Exception as e:
        print(f"❌ Error: {e}")

@app.post("/analyze/en")
async def analyze_english(text: str = Form(...)):
    """English-only endpoint - works perfectly"""
    if not llm:
        return {"error": "Model not loaded"}
    
    start = time.time()
    
    # English-optimized prompt
    prompt = f"""<|system|>
You are a wine expert sommelier. Answer in clear, professional English.
Focus on wine pairings, characteristics, and recommendations.<|im_end|>
<|user|>
{text}<|im_end|>
<|assistant|>
"""
    
    try:
        response = llm(
            prompt,
            max_tokens=150,
            temperature=0.5,
            top_p=0.8,
            stop=["</s>", "\n\n"]
        )
        
        generated = response["choices"][0]["text"].strip()
        elapsed = time.time() - start
        
        logging.info(f"EN Request: {text} | Time: {elapsed:.2f}s")
        
        return {
            "response": generated,
            "time_seconds": round(elapsed, 2),
            "tokens_generated": len(generated.split()),
            "language": "English",
            "model": "TinyLlama 1.1B",
            "note": "Spanish support coming soon"
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze/es")
async def analyze_spanish(text: str = Form(...)):
    """Spanish endpoint with warning about encoding"""
    return {
        "warning": "Spanish model is being upgraded",
        "suggestion": "Please use English endpoint for now: /analyze/en",
        "expected_date": "Next update",
        "current_issue": "Encoding problems with available Spanish models",
        "workaround": "We're acquiring a proper Spanish model"
    }

@app.get("/roadmap")
async def roadmap():
    """Project development roadmap"""
    return {
        "current": {
            "status": "English-only functional version",
            "model": "TinyLlama 1.1B",
            "language": "English (perfect)",
            "encoding": "UTF-8 correct"
        },
        "next_phase": {
            "goal": "Add Spanish support",
            "action": "Acquire Spanish-native model",
            "options": ["Qwen2.5 Spanish", "Gemma-2b", "Spanish-LLaMA"],
            "eta": "1-2 days"
        },
        "future": {
            "prism": "Automatic language routing",
            "features": ["Wine database", "Food pairing AI", "Price analysis"],
            "multilingual": ["Spanish", "French", "Italian", "German"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)  # New clean port
