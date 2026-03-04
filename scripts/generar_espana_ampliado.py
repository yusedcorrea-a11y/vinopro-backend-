#!/usr/bin/env python3
"""
Genera data/espana_ampliado.json con cientos de vinos españoles.
Claves con prefijo esp_ para no colisionar con espana.json.
Uso: python scripts/generar_espana_ampliado.py
"""
import json
import re
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT = DATA_DIR / "espana_ampliado.json"

PAIS = "España"


def slug(s: str) -> str:
    if not s:
        return ""
    t = s.lower().strip()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n"), ("ü", "u")]:
        t = t.replace(a, b)
    t = re.sub(r"[^a-z0-9]+", "_", t)
    return t.strip("_") or "vino"


def vino(nombre, bodega, region, tipo, puntuacion, precio, descripcion=None, notas=None, maridaje=None):
    d = {
        "nombre": nombre,
        "bodega": bodega,
        "region": region,
        "pais": PAIS,
        "tipo": tipo,
        "puntuacion": puntuacion,
        "precio_estimado": precio,
    }
    d["descripcion"] = descripcion or f"Vino {tipo} de {region}, {bodega}."
    d["notas_cata"] = notas or "Equilibrado, buena estructura."
    d["maridaje"] = maridaje or "Carnes, quesos, cocina mediterránea."
    return d


# Lista compacta: (nombre, bodega, region, tipo, puntuacion, precio[, desc, notas, maridaje])
VINOS = [
    # --- RIOJA ---
    ("Marqués de Riscal Reserva", "Marqués de Riscal", "Rioja", "tinto", 90, "12-18€"),
    ("Marqués de Riscal Gran Reserva", "Marqués de Riscal", "Rioja", "tinto", 92, "25-35€"),
    ("CVNE Imperial Gran Reserva", "CVNE", "Rioja", "tinto", 94, "45-60€"),
    ("CVNE Cune Crianza", "CVNE", "Rioja", "tinto", 87, "8-12€"),
    ("La Rioja Alta 890 Gran Reserva", "La Rioja Alta", "Rioja", "tinto", 95, "120-150€"),
    ("La Rioja Alta Ardanza Reserva", "La Rioja Alta", "Rioja", "tinto", 92, "25-32€"),
    ("Muga Reserva", "Bodegas Muga", "Rioja", "tinto", 90, "18-24€"),
    ("Muga Prado Enea Gran Reserva", "Bodegas Muga", "Rioja", "tinto", 94, "55-70€"),
    ("López de Heredia Viña Tondonia Reserva", "López de Heredia", "Rioja", "tinto", 93, "35-45€"),
    ("López de Heredia Viña Gravonia", "López de Heredia", "Rioja", "blanco", 91, "28-35€"),
    ("Ramón Bilbao Reserva", "Ramón Bilbao", "Rioja", "tinto", 88, "12-16€"),
    ("Ramón Bilbao Mirto", "Ramón Bilbao", "Rioja", "tinto", 91, "45-55€"),
    ("Faustino I Gran Reserva", "Faustino", "Rioja", "tinto", 90, "18-25€"),
    ("Faustino V Reserva", "Faustino", "Rioja", "tinto", 87, "10-14€"),
    ("Marqués de Cáceres Crianza", "Marqués de Cáceres", "Rioja", "tinto", 86, "8-11€"),
    ("Marqués de Cáceres Gran Reserva", "Marqués de Cáceres", "Rioja", "tinto", 91, "22-28€"),
    ("Beronia Reserva", "Beronia", "Rioja", "tinto", 88, "12-16€"),
    ("Beronia Gran Reserva", "Beronia", "Rioja", "tinto", 92, "28-35€"),
    ("Campo Viejo Reserva", "Campo Viejo", "Rioja", "tinto", 85, "6-9€"),
    ("El Coto Crianza", "El Coto de Rioja", "Rioja", "tinto", 85, "7-10€"),
    ("Viña Pomal Reserva", "Bodegas Bilbaínas", "Rioja", "tinto", 88, "12-16€"),
    ("Baigorri Crianza", "Baigorri", "Rioja", "tinto", 87, "10-14€"),
    ("Baigorri de Garage", "Baigorri", "Rioja", "tinto", 92, "35-45€"),
    ("Remelluri Reserva", "Granja Remelluri", "Rioja", "tinto", 91, "35-42€"),
    ("Roda I", "Bodega Roda", "Rioja", "tinto", 93, "55-70€"),
    ("Roda Reserva", "Bodega Roda", "Rioja", "tinto", 90, "28-35€"),
    ("Allende Calvario", "Finca Allende", "Rioja", "tinto", 92, "45-55€"),
    ("Artadi Viñas de Gain", "Bodegas Artadi", "Rioja", "tinto", 90, "22-28€"),
    ("Pagos de Labarca Crianza", "Pagos de Labarca", "Rioja", "tinto", 86, "9-13€"),
    ("Bodegas LAN Crianza", "LAN", "Rioja", "tinto", 86, "8-11€"),
    ("Bodegas LAN D-12", "LAN", "Rioja", "tinto", 91, "25-32€"),
    # --- RIBERA DEL DUERO ---
    ("Condado de Haza Crianza", "Condado de Haza", "Ribera del Duero", "tinto", 89, "15-22€"),
    ("Alión", "Bodegas Alión", "Ribera del Duero", "tinto", 93, "55-70€"),
    ("Pesquera Crianza", "Tinto Pesquera", "Ribera del Duero", "tinto", 90, "18-25€"),
    ("Pesquera Janus", "Tinto Pesquera", "Ribera del Duero", "tinto", 94, "80-100€"),
    ("Protos Reserva", "Bodega Protos", "Ribera del Duero", "tinto", 90, "22-28€"),
    ("Protos Gran Reserva", "Bodega Protos", "Ribera del Duero", "tinto", 92, "35-45€"),
    ("Emilio Moro Malleolus", "Emilio Moro", "Ribera del Duero", "tinto", 91, "35-45€"),
    ("Emilio Moro Crianza", "Emilio Moro", "Ribera del Duero", "tinto", 88, "15-20€"),
    ("Hacienda Monasterio", "Hacienda Monasterio", "Ribera del Duero", "tinto", 92, "45-55€"),
    ("Pago de Carraovejas Crianza", "Pago de Carraovejas", "Ribera del Duero", "tinto", 89, "22-28€"),
    ("Pago de Carraovejas Reserva", "Pago de Carraovejas", "Ribera del Duero", "tinto", 92, "40-50€"),
    ("Dominio de Atauta", "Dominio de Atauta", "Ribera del Duero", "tinto", 91, "28-35€"),
    ("Mauro", "Bodegas Mauro", "Ribera del Duero", "tinto", 90, "25-32€"),
    ("Abadía Retuerta Selección Especial", "Abadía Retuerta", "Ribera del Duero", "tinto", 92, "35-45€"),
    ("Arzuaga Reserva", "Bodegas Arzuaga", "Ribera del Duero", "tinto", 89, "25-32€"),
    ("Tridente", "Bodega Tridente", "Ribera del Duero", "tinto", 88, "18-24€"),
    ("Vega Sicilia Único (referencia)", "Vega Sicilia", "Ribera del Duero", "tinto", 98, "350-400€"),
    ("Tionio Crianza", "Bodegas Tionio", "Ribera del Duero", "tinto", 86, "10-14€"),
    ("Viña Sastre Reserva", "Viña Sastre", "Ribera del Duero", "tinto", 91, "30-38€"),
    ("Prado Rey Crianza", "Prado Rey", "Ribera del Duero", "tinto", 87, "12-16€"),
    # --- RUEDA ---
    ("Marqués de Riscal Verdejo", "Marqués de Riscal", "Rueda", "blanco", 88, "8-12€"),
    ("Martinsancho Verdejo", "Martinsancho", "Rueda", "blanco", 90, "12-16€"),
    ("Naia Verdejo", "Bodegas Naia", "Rueda", "blanco", 89, "10-14€"),
    ("Belondrade y Lurton", "Belondrade y Lurton", "Rueda", "blanco", 92, "28-35€"),
    ("José Pariente Verdejo", "José Pariente", "Rueda", "blanco", 89, "10-14€"),
    ("Palacio de Bornos Verdejo", "Palacio de Bornos", "Rueda", "blanco", 86, "7-10€"),
    ("Blanco Nieva Pie Franco", "Blanco Nieva", "Rueda", "blanco", 90, "14-18€"),
    ("Shaya Verdejo", "Bodega Shaya", "Rueda", "blanco", 88, "10-14€"),
    ("Protos Verdejo", "Bodega Protos", "Rueda", "blanco", 87, "8-11€"),
    ("Druide Verdejo", "Bodega Druide", "Rueda", "blanco", 86, "7-10€"),
    # --- RÍAS BAIXAS ---
    ("Martín Códax Albariño", "Martín Códax", "Rías Baixas", "blanco", 88, "10-14€"),
    ("Pazo de Señorans Albariño", "Pazo de Señorans", "Rías Baixas", "blanco", 91, "18-24€"),
    ("Bodegas del Palacio de Fefiñanes", "Palacio de Fefiñanes", "Rías Baixas", "blanco", 90, "16-22€"),
    ("Santiago Ruiz Albariño", "Santiago Ruiz", "Rías Baixas", "blanco", 89, "12-16€"),
    ("Fillaboa Albariño", "Fillaboa", "Rías Baixas", "blanco", 88, "12-16€"),
    ("Terras Gauda Albariño", "Terras Gauda", "Rías Baixas", "blanco", 89, "11-15€"),
    ("Burgans Albariño", "Martin Codax", "Rías Baixas", "blanco", 86, "8-11€"),
    ("Val do Salnés Albariño", "Bodega Val do Salnés", "Rías Baixas", "blanco", 85, "7-10€"),
    ("Pazo de Barrantes Albariño", "Pazo de Barrantes", "Rías Baixas", "blanco", 90, "16-20€"),
    ("Granbazán Ambar Albariño", "Granbazán", "Rías Baixas", "blanco", 87, "10-14€"),
    # --- PRIORAT / MONTSANT ---
    ("Clos Mogador", "Clos Mogador", "Priorat", "tinto", 95, "80-100€"),
    ("Finca Dofí", "Álvaro Palacios", "Priorat", "tinto", 93, "55-70€"),
    ("L'Ermita (referencia)", "Álvaro Palacios", "Priorat", "tinto", 98, "500-800€"),
    ("Mas Doix Prior", "Mas Doix", "Priorat", "tinto", 92, "45-55€"),
    ("Vall Llach Embruix", "Vall Llach", "Priorat", "tinto", 90, "25-32€"),
    ("Terroir Al Límit Les Tosses", "Terroir Al Límit", "Priorat", "tinto", 91, "35-45€"),
    ("Celler de Capçanes Cabrida", "Celler de Capçanes", "Montsant", "tinto", 88, "12-18€"),
    ("Celler de Capçanes Flor del Flor", "Celler de Capçanes", "Montsant", "tinto", 90, "18-24€"),
    ("Joan d'Anguera Finca L'Argata", "Joan d'Anguera", "Montsant", "tinto", 89, "15-20€"),
    ("Acústic Celler Braó", "Acústic Celler", "Montsant", "tinto", 88, "14-18€"),
    # --- PENEDÈS / CAVA ---
    ("Torres Gran Coronas Reserva", "Torres", "Penedès", "tinto", 88, "12-16€"),
    ("Torres Sangre de Toro", "Torres", "Penedès", "tinto", 86, "6-9€"),
    ("Torres Fransola", "Torres", "Penedès", "blanco", 89, "18-24€"),
    ("Jean Leon Chardonnay", "Jean Leon", "Penedès", "blanco", 88, "14-18€"),
    ("Codorníu Cuvée Barcelona", "Codorníu", "Cava", "espumoso", 85, "6-9€"),
    ("Codorníu Reina María Cristina", "Codorníu", "Cava", "espumoso", 88, "12-16€"),
    ("Freixenet Cordon Negro", "Freixenet", "Cava", "espumoso", 84, "5-8€"),
    ("Freixenet Elyssia Gran Cuvée", "Freixenet", "Cava", "espumoso", 88, "14-18€"),
    ("Gramona III Lustros", "Gramona", "Cava", "espumoso", 92, "35-45€"),
    ("Recaredo Terrers", "Recaredo", "Cava", "espumoso", 90, "18-24€"),
    ("Raventós i Blanc de Nit", "Raventós i Blanc", "Cava", "espumoso", 89, "16-22€"),
    ("Juve y Camps Reserva de la Familia", "Juve y Camps", "Cava", "espumoso", 89, "14-18€"),
    ("Castell Sant Antoni Cava Brut", "Castell Sant Antoni", "Cava", "espumoso", 85, "7-10€"),
    # --- JEREZ / MANZANILLA ---
    ("Tío Pepe Fino", "Gonzalez Byass", "Jerez", "blanco", 90, "12-16€"),
    ("La Ina Fino", "Pedro Domecq", "Jerez", "blanco", 89, "10-14€"),
    ("Lustau Fino Jarana", "Lustau", "Jerez", "blanco", 88, "10-14€"),
    ("Lustau Amontillado", "Lustau", "Jerez", "blanco", 90, "14-18€"),
    ("Lustau Oloroso", "Lustau", "Jerez", "blanco", 90, "14-18€"),
    ("La Guita Manzanilla", "Hijos de Rainera Pérez Marín", "Jerez", "blanco", 88, "8-11€"),
    ("Barbadillo Manzanilla", "Barbadillo", "Jerez", "blanco", 87, "7-10€"),
    ("Valdespino Fino Inocente", "Valdespino", "Jerez", "blanco", 91, "16-20€"),
    ("Fernando de Castilla Antique Fino", "Fernando de Castilla", "Jerez", "blanco", 92, "22-28€"),
    ("Hidalgo La Gitana Manzanilla", "Hidalgo", "Jerez", "blanco", 89, "8-12€"),
    # --- TORO ---
    ("Numanthia", "Numanthia", "Toro", "tinto", 93, "55-70€"),
    ("Termanthia", "Numanthia", "Toro", "tinto", 95, "120-150€"),
    ("Faro de Sanabria Crianza", "Bodega Faro", "Toro", "tinto", 87, "10-14€"),
    ("Muruve Reserva", "Bodegas Muruve", "Toro", "tinto", 89, "18-24€"),
    ("Sobreño Crianza", "Bodega Sobreño", "Toro", "tinto", 88, "12-16€"),
    ("Vega Saúco", "Bodega Vega Saúco", "Toro", "tinto", 86, "10-14€"),
    ("Pintia", "Bodega Pintia", "Toro", "tinto", 91, "35-45€"),
    ("D. Ventura", "Bodega D. Ventura", "Toro", "tinto", 87, "12-16€"),
    # --- BIERZO ---
    ("Descendientes de J. Palacios Villa de Corullón", "Descendientes de J. Palacios", "Bierzo", "tinto", 91, "28-35€"),
    ("Castro Ventosa El Castro de Valtuille", "Castro Ventosa", "Bierzo", "tinto", 89, "18-24€"),
    ("Raúl Pérez Ultreia", "Raúl Pérez", "Bierzo", "tinto", 90, "22-28€"),
    ("Dominio de Tares Baltos", "Dominio de Tares", "Bierzo", "tinto", 88, "12-16€"),
    ("Dominio de Tares Cepas Viejas", "Dominio de Tares", "Bierzo", "tinto", 90, "18-24€"),
    ("Petalos del Bierzo", "Descendientes de J. Palacios", "Bierzo", "tinto", 88, "14-18€"),
    ("Luna Beberide Mencía", "Luna Beberide", "Bierzo", "tinto", 86, "8-12€"),
    ("Tilenus Crianza", "Bodega Tilenus", "Bierzo", "tinto", 87, "10-14€"),
    # --- NAVARRA ---
    ("Chivite Colección 125 Reserva", "Bodegas Chivite", "Navarra", "tinto", 92, "45-55€"),
    ("Chivite Gran Feudo Reserva", "Bodegas Chivite", "Navarra", "tinto", 88, "12-16€"),
    ("Señorío de Sarria Viña del Perdon", "Señorío de Sarria", "Navarra", "tinto", 86, "8-11€"),
    ("Ochoa Reserva", "Bodega Ochoa", "Navarra", "tinto", 88, "12-16€"),
    ("Ochoa Moscatel", "Bodega Ochoa", "Navarra", "blanco", 87, "10-14€"),
    ("Gran Feudo Rosado", "Bodegas Chivite", "Navarra", "rosado", 85, "6-9€"),
    ("Señorío de Sarria Garnacha", "Señorío de Sarria", "Navarra", "tinto", 85, "7-10€"),
    # --- SOMONTANO ---
    ("Enate Reserva", "Enate", "Somontano", "tinto", 89, "18-24€"),
    ("Enate Chardonnay", "Enate", "Somontano", "blanco", 88, "12-16€"),
    ("Viñas del Vero La Miranda", "Viñas del Vero", "Somontano", "tinto", 87, "10-14€"),
    ("Bodega Pirineos Gewürztraminer", "Bodega Pirineos", "Somontano", "blanco", 86, "8-11€"),
    ("Lalanne Crianza", "Bodegas Lalanne", "Somontano", "tinto", 86, "9-12€"),
    # --- CAMPO DE BORJA / CALATAYUD ---
    ("Borsao Tres Picos", "Bodegas Borsao", "Campo de Borja", "tinto", 89, "10-14€"),
    ("Borsao Berola", "Bodegas Borsao", "Campo de Borja", "tinto", 87, "8-11€"),
    ("Alto Moncayo", "Alto Moncayo", "Campo de Borja", "tinto", 91, "22-28€"),
    ("Ateca Honoro Vera", "Bodega Ateca", "Calatayud", "tinto", 86, "6-9€"),
    ("Breca Garnacha", "Bodega Breca", "Calatayud", "tinto", 88, "12-16€"),
    ("Evohé Garnacha", "Evohé", "Calatayud", "tinto", 87, "8-11€"),
    # --- VALENCIA / UTIEL-REQUENA / ALICANTE ---
    ("Mustiguillo Finca Terrerazo", "El Terrerazo", "Utiel-Requena", "tinto", 91, "28-35€"),
    ("Chozas Carrascal", "Chozas Carrascal", "Utiel-Requena", "tinto", 90, "22-28€"),
    ("Vega Tolosa", "Vega Tolosa", "Utiel-Requena", "tinto", 87, "10-14€"),
    ("Bodega Mustiguillo Mestizaje", "El Terrerazo", "Utiel-Requena", "tinto", 88, "14-18€"),
    ("Enrique Mendoza Estrecho", "Enrique Mendoza", "Alicante", "tinto", 89, "18-24€"),
    ("Fondillón Enrique Mendoza", "Enrique Mendoza", "Alicante", "tinto", 90, "25-32€"),
    ("Vergel Monastrell", "Bodega Vergel", "Alicante", "tinto", 86, "8-11€"),
    # --- LA MANCHA / VALDEPEÑAS ---
    ("Finca Antigua Crianza", "Finca Antigua", "La Mancha", "tinto", 86, "8-11€"),
    ("Pagos del Rey Reserva", "Pagos del Rey", "Ribera del Duero", "tinto", 88, "12-16€"),
    ("Vega Tolosa La Mancha", "Vega Tolosa", "La Mancha", "tinto", 85, "6-9€"),
    ("Los Llanos Valdepeñas Crianza", "Los Llanos", "Valdepeñas", "tinto", 85, "6-9€"),
    ("Viña Albali Reserva", "Felix Solis", "Valdepeñas", "tinto", 86, "7-10€"),
    ("Casa de la Viña Reserva", "Casa de la Viña", "Valdepeñas", "tinto", 85, "6-8€"),
    # --- RIBEIRA SACRA / RIBEIRO ---
    ("Guímaro Ribeira Sacra", "Guímaro", "Ribeira Sacra", "tinto", 88, "14-18€"),
    ("D. Ventura Ribeira Sacra", "D. Ventura", "Ribeira Sacra", "tinto", 87, "12-16€"),
    ("Adega Algueira", "Algueira", "Ribeira Sacra", "tinto", 89, "16-20€"),
    ("Viña Meín Ribeiro", "Viña Meín", "Ribeiro", "blanco", 87, "10-14€"),
    ("Emilio Rojo Ribeiro", "Emilio Rojo", "Ribeiro", "blanco", 90, "18-24€"),
    # --- COSTERS DEL SEGRE / TERRA ALTA / EMPORDÀ ---
    ("Raimat Abadía", "Raimat", "Costers del Segre", "tinto", 88, "12-16€"),
    ("Raimat Chardonnay", "Raimat", "Costers del Segre", "blanco", 86, "8-11€"),
    ("Celler Bàrbara Forés Terra Alta", "Bàrbara Forés", "Terra Alta", "blanco", 88, "10-14€"),
    ("Celler Piñol Ludovicus", "Celler Piñol", "Terra Alta", "tinto", 87, "10-14€"),
    ("Espelt Empordà", "Espelt", "Empordà", "tinto", 86, "8-11€"),
    ("Perelada 5 Finques", "Castillo de Perelada", "Empordà", "tinto", 88, "14-18€"),
    # --- V.T. CASTILLA Y LEÓN / OTROS ---
    ("Abadía de San Campio", "Abadía de San Campio", "V.T. Castilla y León", "tinto", 86, "8-11€"),
    ("Bodega Gormaz Senda del Oro", "Bodega Gormaz", "Ribera del Duero", "tinto", 85, "7-10€"),
    ("Legaris Crianza", "Legaris", "Ribera del Duero", "tinto", 87, "12-16€"),
    ("Carmelo Rodero Crianza", "Carmelo Rodero", "Ribera del Duero", "tinto", 88, "14-18€"),
    ("Prado de Oliva", "Prado de Oliva", "V.T. Castilla y León", "tinto", 86, "9-12€"),
]


def main():
    out = {}
    for t in VINOS:
        nombre, bodega, region, tipo, puntuacion, precio = t[0], t[1], t[2], t[3], t[4], t[5]
        desc = notas = maridaje = None
        if len(t) > 6:
            desc = t[6]
        if len(t) > 7:
            notas = t[7]
        if len(t) > 8:
            maridaje = t[8]
        entry = vino(nombre, bodega, region, tipo, puntuacion, precio, desc, notas, maridaje)
        key = "esp_" + slug(region) + "_" + slug(bodega) + "_" + slug(nombre)
        if len(key) > 90:
            key = key[:90]
        while key in out:
            key = key.rstrip("_0123456789") + "_" + str(len(out))
        out[key] = entry

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[OK] Generado {OUTPUT} con {len(out)} vinos españoles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
