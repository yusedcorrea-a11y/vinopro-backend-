from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="VINO PRO - Servidor Emergencia")

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    # Respuesta de emergencia SIMULADA mientras Ollama se instala
    return JSONResponse(content={
        "status": "servidor_emergencia",
        "mensaje": "Ollama instalándose. Modelos locales (Phi-2, TinyLlama) fallaron.",
        "datos_simulados": {
            "nombre": text.split(".")[0] if "." in text else text[:30],
            "bodega": "extracción pendiente",
            "año": "2023",
            "color": "simulado",
            "aroma": "simulado"
        },
        "proximo_paso": "Ejecutar 'ollama pull llama3.2:3b' cuando termine instalación"
    })

if __name__ == "__main__":
    print("🆘 SERVIDOR DE EMERGENCIA - Esperando Ollama...")
    print("🌐 Escuchando en http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
