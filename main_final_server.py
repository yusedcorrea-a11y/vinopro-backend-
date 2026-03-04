from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from llama_cpp import Llama
import uvicorn

app = FastAPI(title="VINO PRO - Nuclear")

MODEL_PATH = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
print("Modelo Phi-2 - Modo Nuclear Activado")

@app.post("/analyze/text")
async def analyze_text(request: Request):
    try:
        data = await request.form()
        texto = data.get("text", "").strip()
        
        if not texto:
            return JSONResponse(content={"error": "No text provided"})
        
        print(f"\n? PETICIÓN NUCLEAR: {texto[:30]}...")
        
        # Configuración AGGRESIVA
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,  # MUY pequeño para forzar atención
            n_threads=1,
            verbose=False
        )
        
        # PROMPT NUCLEAR - ORDENES DIRECTAS, SIN MARGEN
        prompt = f"""ANÁLISIS DE VINO - ORDEN DIRECTA:

TEXTO A ANALIZAR: "{texto}"

RESPONDE INMEDIATAMENTE con estos 5 campos:

color: [ESCRIBE AQUÍ EL COLOR]
aroma: [ESCRIBE AQUÍ LOS AROMAS]
sabor: [ESCRIBE AQUÍ EL SABOR]
cuerpo: [ESCRIBE AQUÍ EL CUERPO]
final: [ESCRIBE AQUÍ EL FINAL]

NO escribas ejercicios, NO expliques, NO añadas "Solution:", NO hagas follow-up.
SOLO los 5 campos arriba. EMPIEZA DIRECTAMENTE con "color:"""
        
        # Forzar inicio con "color:"
        respuesta = llm(
            prompt, 
            max_tokens=150,
            temperature=0.0,  # CERO creatividad
            top_p=0.1,  # Muy restrictivo
            stop=["\n\n", "Solution:", "Follow-up"]
        )
        
        texto_respuesta = respuesta["choices"][0]["text"].strip()
        print(f"?? RESPUESTA CRUDA: {texto_respuesta}")
        
        # Parseo ULTRA simple
        datos = {}
        lineas_actuales = [f"color:{texto_respuesta}"] if texto_respuesta.startswith("color:") else []
        lineas_actuales.extend(texto_respuesta.split('\n'))
        
        for linea in lineas_actuales:
            linea = linea.strip()
            if ':' in linea:
                clave_valor = linea.split(':', 1)
                if len(clave_valor) == 2:
                    clave = clave_valor[0].strip().lower()
                    valor = clave_valor[1].strip()
                    if clave in ['color', 'aroma', 'sabor', 'cuerpo', 'final'] and valor:
                        datos[clave] = valor
        
        del llm
        
        if datos:
            return JSONResponse(content={
                "exito": True,
                "datos": datos,
                "nota": "Extracción nuclear exitosa",
                "respuesta_original": texto_respuesta[:100] + "..." if len(texto_respuesta) > 100 else texto_respuesta
            })
        else:
            return JSONResponse(content={
                "exito": False,
                "error": "Phi-2 en modo educativo rebelde",
                "respuesta_rebelde": texto_respuesta[:200],
                "solucion_recomendada": "Cambiar a Qwen2.5-3B u OpenAI API"
            })
        
    except Exception as e:
        return JSONResponse(content={"exito": False, "error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
