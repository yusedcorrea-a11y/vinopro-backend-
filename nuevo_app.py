from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# Cargar diccionario de vinos
with open('vinos_diccionario.json', 'r', encoding='utf-8') as f:
    VINOS_MUNDIALES = json.load(f)

print(f'✅ VINOS_MUNDIALES cargado con {len(VINOS_MUNDIALES)} vinos')

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "VINO PRO WORLD EDITION",
        "version": "4.0",
        "vinos_en_db": len(VINOS_MUNDIALES)
    }

@app.post("/analyze/text")
def analyze_wine(texto: str = Form(...)):
    texto_lower = texto.lower().strip()
    
    # Buscar vino en el diccionario
    for key, vino in VINOS_MUNDIALES.items():
        if key in texto_lower or vino['nombre'].lower() in texto_lower:
            return {
                "success": True,
                "analysis": vino
            }
    
    # Si no se encuentra, análisis genérico
    tipo = "tinto" if "tinto" in texto_lower else "blanco"
    return {
        "success": True,
        "analysis": {
            "nombre": texto,
            "bodega": "No especificada",
            "region": "Por determinar",
            "pais": "España",
            "tipo": tipo,
            "puntuacion": 70,
            "precio_estimado": "14-26€",
            "descripcion": f"Análisis de {texto}. Vino no encontrado en base de datos."
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
