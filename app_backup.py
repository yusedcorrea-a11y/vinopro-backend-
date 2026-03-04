import json
import os
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

# Inicializar app
app = FastAPI(title="VINO PRO IA", description="API de análisis de vinos")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar diccionario de vinos
def cargar_diccionario_vinos():
    """Carga el diccionario de vinos desde el archivo JSON"""
    ruta_json = os.path.join(os.path.dirname(__file__), "vinos_diccionario.json")
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            vinos = json.load(f)
            print(f"✅ VINOS_MUNDIALES cargado con {len(vinos)} vinos")
            return vinos
    except FileNotFoundError:
        print("⚠️ Archivo vinos_diccionario.json no encontrado. Usando diccionario vacío.")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return {}

# Cargar vinos al iniciar
VINOS_MUNDIALES = cargar_diccionario_vinos()

@app.get("/")
def root():
    """Endpoint de verificación"""
    return {
        "status": "ok",
        "service": "VINO PRO WORLD EDITION",
        "version": "4.0",
        "vinos_en_db": len(VINOS_MUNDIALES)
    }

@app.post("/analyze/text")
def analyze_wine(texto: str = Form(...)):
    """
    Analiza un vino por texto
    - Busca en el diccionario por nombre o palabras clave
    - Si no encuentra, devuelve análisis genérico
    """
    texto_lower = texto.lower().strip()
    
    # Buscar vino en el diccionario (búsqueda inteligente)
    palabras_busqueda = [p for p in texto_lower.split() if len(p) > 3]  # Ignorar palabras cortas
    vino_encontrado = None
    mejor_coincidencia = 0
    mejor_key = None
    
    # Primera pasada: buscar por nombre exacto o key
    for key, vino in VINOS_MUNDIALES.items():
        nombre_vino = vino['nombre'].lower()
        
        # Coincidencia exacta del nombre
        if nombre_vino == texto_lower:
            print(f"✓ Coincidencia exacta: {vino['nombre']}")
            return {
                "success": True,
                "analysis": vino
            }
        
        # Nombre contenido en la búsqueda
        if nombre_vino in texto_lower:
            print(f"✓ Nombre contenido: {vino['nombre']}")
            return {
                "success": True,
                "analysis": vino
            }
    
    # Segunda pasada: buscar por palabras clave
    for key, vino in VINOS_MUNDIALES.items():
        nombre_vino = vino['nombre'].lower()
        coincidencias = 0
        
        for palabra in palabras_busqueda:
            if palabra in nombre_vino:
                coincidencias += 1
        
        # Bonus: si la búsqueda contiene parte del nombre de bodega
        bodega_lower = vino['bodega'].lower() if vino['bodega'] != "No especificada" else ""
        for palabra in palabras_busqueda:
            if palabra in bodega_lower:
                coincidencias += 0.5  # Peso medio para la bodega
        
        # Bonus especial para "Valbuena" (caso específico)
        if "valbuena" in texto_lower and "valbuena" in nombre_vino:
            coincidencias += 2
        
        if coincidencias > mejor_coincidencia:
            mejor_coincidencia = coincidencias
            vino_encontrado = vino
            mejor_key = key
    
    # Si encontramos una buena coincidencia (al menos 1 palabra clave)
    if vino_encontrado and mejor_coincidencia >= 1:
        print(f"✓ Coincidencia por palabras clave ({mejor_coincidencia}): {vino_encontrado['nombre']}")
        return {
            "success": True,
            "analysis": vino_encontrado
        }
    
    # Si no se encuentra, análisis genérico
    print(f"✗ Vino no encontrado: '{texto}'. Usando análisis genérico.")
    
    # Detectar tipo por palabras clave
    tipo = "tinto"
    palabras_tinto = ["tinto", "rojo", "crianza", "reserva", "gran reserva"]
    palabras_blanco = ["blanco", "blanco", "albariño", "verdejo", "rueda"]
    
    texto_lower = texto.lower()
    for p in palabras_blanco:
        if p in texto_lower:
            tipo = "blanco"
            break
    
    # Detectar posible región
    region = "Por determinar"
    regiones = ["ribera", "rioja", "toro", "bierzo", "priorat", "rueda", "rias baixas", "jerez", "cava"]
    for r in regiones:
        if r in texto_lower:
            region = r.title()
            break
    
    return {
        "success": True,
        "analysis": {
            "nombre": texto,
            "bodega": "No especificada",
            "region": region,
            "pais": "España",
            "tipo": tipo,
            "puntuacion": 85,
            "precio_estimado": "15-30€",
            "descripcion": f"Análisis genérico de {texto}. Para un análisis más preciso, prueba con un vino de nuestra base de datos."
        }
    }

@app.get("/vinos")
def listar_vinos():
    """Lista todos los vinos disponibles"""
    return {
        "total": len(VINOS_MUNDIALES),
        "vinos": [
            {
                "key": key,
                "nombre": vino["nombre"],
                "bodega": vino["bodega"],
                "region": vino["region"],
                "puntuacion": vino["puntuacion"]
            }
            for key, vino in VINOS_MUNDIALES.items()
        ]
    }

@app.get("/buscar")
def buscar_vino(q: str):
    """Busca vinos por nombre o bodega"""
    q_lower = q.lower().strip()
    resultados = []
    
    for key, vino in VINOS_MUNDIALES.items():
        if q_lower in vino['nombre'].lower() or q_lower in vino['bodega'].lower():
            resultados.append({
                "key": key,
                "nombre": vino["nombre"],
                "bodega": vino["bodega"],
                "region": vino["region"],
                "puntuacion": vino["puntuacion"]
            })
    
    return {
        "query": q,
        "resultados": len(resultados),
        "vinos": resultados
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor VINO PRO IA...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
