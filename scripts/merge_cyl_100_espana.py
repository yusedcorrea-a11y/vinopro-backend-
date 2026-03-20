# -*- coding: utf-8 -*-
"""Inserta 100 vinos de Castilla y León en data/espana.json (claves cyl_*). Ejecutar desde raíz: python scripts/merge_cyl_100_espana.py"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ESPANA = ROOT / "data" / "espana.json"


def w(
    nombre: str,
    bodega: str,
    region: str,
    tipo: str,
    punt: int,
    precio: str,
    desc: str,
    notas: str = "Fruta madura, especias y roble equilibrado.",
    maridaje: str = "Carnes rojas, embutidos y quesos curados.",
) -> dict:
    return {
        "nombre": nombre,
        "bodega": bodega,
        "region": region,
        "pais": "España",
        "tipo": tipo,
        "puntuacion": punt,
        "precio_estimado": precio,
        "descripcion": desc,
        "notas_cata": notas,
        "maridaje": maridaje,
    }


NUEVOS: dict[str, dict] = {
    # —— Ribera del Duero (marcas prioritarias) ——
    "cyl_malleolus": w("Malleolus", "Emilio Moro", "Ribera del Duero", "tinto", 93, "35-55€", "Línea de parcelas viejas de la familia Moro; Tinto Fino de guarda.", "Fruta negra, especias nobles, roble fino, final largo.", "Cordero lechal, vaca madurada, quesos fuertes"),
    "cyl_emilio_moro_el_mago": w("El Mago", "Emilio Moro", "Ribera del Duero", "tinto", 88, "12-18€", "Joven afrutado de la casa Moro; muy presente en hostelería.", "Frambuesa, taninos suaves, fácil de beber.", "Pizza, tapas, hamburguesa"),
    "cyl_emilio_moro_finca_resalso": w("Finca Resalso", "Emilio Moro", "Ribera del Duero", "tinto", 89, "14-22€", "Crianza del viñedo homónimo; equilibrio fruta-madera.", "Ciruela, vainilla, tabaco suave.", "Pasta, costillas, quesos semicurados"),
    "cyl_valduero_crianza": w("Valduero Crianza", "Bodegas Valduero", "Ribera del Duero", "tinto", 88, "15-24€", "Clásico de Gumiel de Izán; Ribera seria por precio.", "Fruta negra, cuero ligero, taninos pulidos.", "Lechazo, guisos de carne"),
    "cyl_valduero_una_cepa": w("Una Cepa", "Bodegas Valduero", "Ribera del Duero", "tinto", 91, "28-45€", "Selección de viñedo singular; profundidad y capacidad de guarda.", "Mora, grafito, especias.", "Solomillo, caza menor"),
    "cyl_valsotillo_reserva": w("Valsotillo Reserva", "Ismael Arroyo (Valsotillo)", "Ribera del Duero", "tinto", 90, "22-38€", "Sotillo de la Ribera; crianzas largas y terruño clásico.", "Fruta confitada, tabaco, taninos maduros.", "Cordero asado, cocido montañés"),
    "cyl_finca_villacreces": w("Finca Villacreces", "Finca Villacreces", "Ribera del Duero", "tinto", 92, "35-60€", "Parcela junto al Duero; ensamblaje con variedades bordalesas.", "Cassis, violeta, roble elegante.", "Pato, magret, queso de oveja"),
    "cyl_primer_paso": w("Primer Paso", "Finca Villacreces", "Ribera del Duero", "tinto", 88, "16-26€", "Segunda etiqueta; más frutal y para beber antes.", "Fruta roja, especias dulces, taninos finos.", "Lasaña, chorizo a la sidra"),
    "cyl_mibal_crianza": w("Mibal Crianza", "Bodegas Mibal", "Ribera del Duero", "tinto", 87, "12-20€", "Proyecto de la familia García Viadero; buena RCP.", "Cereza negra, regaliz, roble suave.", "Tapas, morcilla, hamburguesa"),
    "cyl_cepa21_hito": w("Hito", "Cepa 21", "Ribera del Duero", "tinto", 89, "14-22€", "Bodega de los Moro en Castrillo; crianza muy difundida.", "Fruta madura, chocolate suave, redondo.", "Pizza, carne picada"),
    "cyl_cepa21_origen": w("Origen", "Cepa 21", "Ribera del Duero", "tinto", 87, "10-16€", "Línea de entrada; Tinto Fino directo.", "Frambuesa, vainilla ligera.", "Empanada, picoteo"),
    "cyl_linaje_garsea": w("Linaje Garsea", "Bodegas Linaje Garsea", "Ribera del Duero", "tinto", 86, "9-15€", "Ribera económica de Aranda; presencia en retail.", "Fruta roja, especias suaves.", "Cocido, lentejas"),
    "cyl_felix_callejo_reserva": w("Felix Callejo Reserva", "Felix Callejo", "Ribera del Duero", "tinto", 92, "35-55€", "Sotillo; potencia y carnosidad característica.", "Fruta negra, humo, taninos densos.", "Chuletón, jabalí"),
    "cyl_felix_callejo_crianza": w("Felix Callejo Crianza", "Felix Callejo", "Ribera del Duero", "tinto", 90, "22-35€", "Crianza clásica de la casa.", "Ciruela, clavo, vainilla.", "Cordero, carrillera"),
    "cyl_los_astrales_angel": w("Los Astrales Ángel", "Los Astrales", "Ribera del Duero", "tinto", 88, "14-22€", "Proyecto de la familia García en la Ribera.", "Fruta madura, taninos firmes.", "Brasa, migas, embutido"),
    "cyl_comenge_reserva": w("Comenge Reserva", "Bodegas Comenge", "Ribera del Duero", "tinto", 89, "18-30€", "Curiel; enología precisa y estilo moderno.", "Arándano, grafito, roble fino.", "Pichón, pasta rellena"),
    "cyl_dehesa_canonigos_reserva": w("Dehesa de los Canónigos Reserva", "Dehesa de los Canónigos", "Ribera del Duero", "tinto", 91, "28-48€", "Peñafiel; Ribera de guarda y clasicismo.", "Fruta negra, cuero, tabaco, largo.", "Caza, asados, quesos fuertes"),
    "cyl_pagos_carraovejas_crianza": w("Pagos de Carraovejas Crianza", "Pagos de Carraovejas", "Ribera del Duero", "tinto", 92, "30-50€", "Referente de Peñafiel; mezcla clásica según añada.", "Mora, especias, roble cremoso.", "Rabo de toro, queso de oveja"),
    "cyl_aldonia_crianza": w("Aldonia Crianza", "Bodegas Aldonia", "Ribera del Duero", "tinto", 87, "12-20€", "Aranda; Ribera honesta por precio.", "Fruta roja, taninos medios.", "Callos, fabada"),
    "cyl_condado_haza_crianza": w("Condado de Haza Crianza", "Condado de Haza", "Ribera del Duero", "tinto", 90, "22-35€", "Proyecto de Alejandro Fernández; estilo potente.", "Fruta negra, vainilla, taninos maduros.", "Entrecot, quesos"),
    "cyl_mil_cantos": w("Mil Cantos", "Mil Cantos", "Ribera del Duero", "tinto", 88, "14-24€", "Proyecto independiente; fruta pura y poco maquillaje.", "Cereza, pimienta rosa, mineral.", "Arroz meloso, mediterráneo"),
    "cyl_montecillo_gran_reserva_rd": w("Montecillo Gran Reserva", "Bodegas Montecillo", "Ribera del Duero", "tinto", 90, "25-40€", "Grupo Faustino en Ribera; crianzas largas.", "Fruta madura, tabaco, cuero.", "Caza, asados"),
    "cyl_mauro_vs": w("Mauro Vendimia Seleccionada", "Mauro", "V.T. Castilla y León", "tinto", 92, "40-70€", "Proyecto de Mariano García en Tudela de Duero; selección de terruño.", "Densidad, especias, estructura amplia.", "Guisos de invierno, carnes rojas"),
    "cyl_basconcillos_crianza": w("Dominio Basconcillos Crianza", "Bodegas Basconcillos", "Ribera del Duero", "tinto", 88, "16-28€", "Tubilla del Lago; buena presencia en exportación.", "Frambuesa, regaliz, roble equilibrado.", "Pasta, parrilla"),
    "cyl_atalayas_golban": w("Atalayas de Golbán", "Atalayas de Golbán", "Ribera del Duero", "tinto", 89, "18-32€", "Gumiel de Izán; fruta seria.", "Mora, cacao, taninos sedosos.", "Cordero, hamburguesa premium"),
    "cyl_balbas_crianza": w("Balbás Crianza", "Bodegas Balbás", "Ribera del Duero", "tinto", 88, "14-24€", "La Horra; bodega histórica de la Ribera.", "Fruta negra, especias, roble integrado.", "Carnes, embutidos"),
    "cyl_balbas_reserva": w("Balbás Reserva", "Bodegas Balbás", "Ribera del Duero", "tinto", 90, "22-38€", "Reserva estructurada desde viñedos de La Horra.", "Ciruela, tabaco, final largo.", "Asados, quesos curados"),
    "cyl_valtravieso_crianza": w("Valtravieso Crianza", "Bodegas Valtravieso", "Ribera del Duero", "tinto", 87, "12-22€", "Peñafiel; línea comercial sólida.", "Fruta roja, roble suave.", "Tapas, pizza"),
    "cyl_garmon": w("Garmón", "Garmón Continental", "Ribera del Duero", "tinto", 93, "45-80€", "Proyecto de Mariano García; Ribera fina y elegante.", "Fruta negra, mineral, taninos de seda.", "Caza, vaca, quesos"),
    "cyl_lantuen": w("Lantuén", "Bodegas Lantuén", "Ribera del Duero", "tinto", 86, "10-18€", "Ribera asequible de zona de Aranda.", "Fruta roja directa, taninos ligeros.", "Cocido, menús del día"),
    "cyl_bardos_reserva": w("Bardos Reserva", "Bodegas Bardos (Milcampos)", "Ribera del Duero", "tinto", 89, "18-32€", "La Aguilera; proyecto serio de la familia.", "Fruta negra, especias, roble fino.", "Cordero, setas"),
    "cyl_milcampos_milcampos": w("Milcampos Crianza", "Bodegas Milcampos", "Ribera del Duero", "tinto", 87, "12-20€", "Ribera popular de La Aguilera.", "Frambuesa, vainilla suave.", "Tapas, pasta"),
    "cyl_honorato_calvo": w("Honorato Calvo", "Bodegas Honorato Calvo", "Ribera del Duero", "tinto", 86, "10-16€", "Santibáñez de Ecla; tradición local.", "Fruta roja, especias suaves.", "Embutido, queso"),
    "cyl_matarromera_pago": w("Matarromera Pago de las Solanas", "Bodegas Matarromera", "Ribera del Duero", "tinto", 91, "28-45€", "Selección de pago de Olivares de Duero.", "Fruta madura, mineral, estructura.", "Vacío, quesos"),
    "cyl_ylanza_crianza": w("Ylanzo Crianza", "Bodegas Ylanzo", "Ribera del Duero", "tinto", 85, "8-14€", "Ribera de entrada; presencia en grandes superficies.", "Fruta roja simple, taninos suaves.", "Menú diario, pizza"),
    "cyl_cillar_silos_psi": w("PSI", "Dominio de Pingus (PSI)", "Ribera del Duero", "tinto", 90, "22-38€", "Segunda línea del proyecto Pingus; accesible y serio.", "Fruta pura, especias, elegancia.", "Cordero, pasta rellena"),
    # —— Rueda (Verdejo y blancos; marcas) ——
    "cyl_naia_verdejo": w("Naia", "Bodegas Naia", "Rueda", "blanco", 87, "8-14€", "Verdejo joven muy difundido; frescor y precio contenido.", "Hierbas, cítricos, marco refrescante.", "Pescado frito, ensalada, aperitivo"),
    "cyl_shaya_verdejo": w("Shaya", "Gil Family Estates", "Rueda", "blanco", 88, "10-16€", "Verdejo de proyecto Gil en Rueda; aromático.", "Pomelo, melón, final limpio.", "Sushi, ceviche, queso fresco"),
    "cyl_garcigrande_verdejo": w("GarciGrande Verdejo", "GarciGrande", "Rueda", "blanco", 86, "7-12€", "Verdejo de gran volumen en retail español.", "Hierba, lima, bebible.", "Ensalada, tortilla"),
    "cyl_menade_verdejo": w("Menade Verdejo", "Menade", "Rueda", "blanco", 89, "12-20€", "Familia Sanz; enfoque ecológico y fruta limpia.", "Cítricos, flor blanca, mineral.", "Marisco, arroz blanco"),
    "cyl_mocen_verdejo": w("Mocén Verdejo", "Yllera (Mocén)", "Rueda", "blanco", 87, "8-14€", "Clásico de súper y hostelería en Castilla y León.", "Manzana verde, hierbas.", "Tapas, pavo"),
    "cyl_ossian_vinas_viejas": w("Ossian Viñas Viejas", "Ossian", "V.T. Castilla y León", "blanco", 92, "35-55€", "Verdejo viejo de vaso; crianza en madera, referencia de autor.", "Melocotón, miel seca, volumen y acidez.", "Bacalao, queso curado, marisquería"),
    "cyl_blanco_nieva_sauvignon": w("Blanco Nieva Sauvignon Blanc", "Martínez Bujanda", "Rueda", "blanco", 86, "8-14€", "Blanco aromático de la gama Nieva.", "Maracuyá, hierba, fresco.", "Ensaladas, pescado blanco"),
    "cyl_palarea_verdejo": w("Palarea Verdejo", "Bodegas Palarea", "Rueda", "blanco", 85, "7-12€", "Verdejo sencillo de Rueda.", "Lima, hierbas.", "Aperitivo, fritura"),
    "cyl_angel_lorenzo_verdejo": w("Angel Lorenzo Cachazo Verdejo", "Angel Lorenzo Cachazo", "Rueda", "blanco", 88, "10-18€", "Familia con viñedo en La Seca; Verdejo serio por precio.", "Pomelo, salinidad ligera.", "Percebes, queso de cabra"),
    "cyl_montepedroso_verdejo": w("Finca Montepedroso Verdejo", "Finca Montepedroso", "Rueda", "blanco", 89, "14-24€", "Proyecto de José Pariente en Rueda; mineral.", "Hierbas, piedra húmeda, largo.", "Pulpo, sushi"),
    "cyl_jose_pariente_sauvignon": w("José Pariente Sauvignon Blanc", "José Pariente", "Rueda", "blanco", 88, "12-20€", "Blanco aromático de la casa referente en Rueda.", "Maracuyá, cítricos, frescor.", "Ceviche, ensaladas, marisco"),
    "cyl_protos_verdejo": w("Protos Verdejo", "Bodegas Protos", "Rueda", "blanco", 88, "10-18€", "Blanco del histórico grupo de Peñafiel; buena distribución.", "Manzana, hierbas, equilibrado.", "Pescado plancha, arroz"),
    "cyl_yllera_verdejo": w("Yllera Verdejo", "Yllera", "Rueda", "blanco", 86, "6-12€", "Verdejo de alta rotación en la comunidad.", "Cítricos, ligero.", "Tapeo, menú"),
    "cyl_castillo_aresan_verdejo": w("Castillo de Aresan Verdejo", "Castillo de Aresan", "Rueda", "blanco", 85, "6-11€", "Marca económica habitual en cadenas.", "Lima, hierba fresca.", "Comida informal"),
    "cyl_libalis_verdejo": w("Libalis Verdejo", "Bodegas Mucientes", "Rueda", "blanco", 87, "9-15€", "Línea joven del grupo; buen aperitivo.", "Flor blanca, cítricos.", "Ensalada, pescado"),
    "cyl_el_pacto_blanco": w("El Pacto", "Comando G / viticultores", "V.T. Castilla y León", "blanco", 90, "22-40€", "Blanco de altitud y viña vieja en Sierra de Gredos (CyL).", "Pomelo, sal, textura.", "Trucha, queso afilado"),
    "cyl_oliver_verdejo": w("Oliver Verdejo", "Bodegas Oliver", "Rueda", "blanco", 86, "7-13€", "Verdejo de consumo diario.", "Manzana, hierbas.", "Arroz, pollo"),
    "cyl_valdeguerra_verdejo": w("Valdeguerra Verdejo", "Bodegas Valdeguerra", "Rueda", "blanco", 85, "6-11€", "Rueda asequible para eventos.", "Cítricos simples.", "Picoteo"),
    "cyl_marques_grinan_verdejo": w("Marqués de Griñón Verdejo", "Pagos de Familia (Domecq)", "Rueda", "blanco", 87, "10-16€", "Verdejo de grupo grande; presencia nacional.", "Melón, hierbas.", "Pescado, pasta blanca"),
    "cyl_transicion_verdejo": w("Transición Verdejo", "Bodegas de la Rueda (referencia ecológica)", "Rueda", "blanco", 86, "9-15€", "Línea ecológica de distribución creciente.", "Pomelo, nota herbácea.", "Verduras, pescado"),
    "cyl_dos_maderas_blanco": w("Dos Maderas Blanco", "Williams & Humbert / Rueda", "Rueda", "blanco", 88, "14-24€", "Crianza en barrica y soleras; proyecto singular.", "Miel, fruta confitada, especias.", "Foie, queso azul suave"),
    "cyl_verdejo_barrica_generico": w("Verdejo Barrica (Rueda)", "Varios productores", "Rueda", "blanco", 87, "12-22€", "Estilo cremoso con paso por roble; común en cartas.", "Melocotón, vainilla, untuoso.", "Risotto, pescado graso"),
    # —— Toro ——
    "cyl_maurodos_san_roman": w("San Román", "Maurodos", "Toro", "tinto", 91, "25-45€", "Referente de Toro moderno; Tinta de Toro potente.", "Mora, chocolate, taninos firmes.", "Cordero, vaca"),
    "cyl_elias_mora": w("Elias Mora", "Bodegas Elias Mora", "Toro", "tinto", 89, "18-32€", "Toro clásico de San Román de Hornija.", "Fruta negra, especias, mineral.", "Cecina, guisos"),
    "cyl_colegiata_torres": w("Colegiata", "Bodegas Fariña", "Toro", "tinto", 87, "12-22€", "Toro accesible y muy conocido.", "Ciruela, taninos medios.", "Embutido, pasta"),
    "cyl_matsu_el_picaro": w("Matsu El Pícaro", "Matsu (Vintae)", "Toro", "tinto", 88, "10-18€", "Proyecto con etiquetas de añada; joven afrutado.", "Mora, licoroso suave.", "Hamburguesa, costillas"),
    "cyl_almirez": w("Almirez", "Teso La Monja (Eguren)", "Toro", "tinto", 92, "35-60€", "Selección de viñedo en Toro; concentración extrema.", "Fruta negra densa, especias, largo.", "Chuletón, caza"),
    "cyl_gago": w("Gago", "Telmo Rodríguez", "Toro", "tinto", 90, "18-32€", "Toro de perfil fresco y moderno.", "Frambuesa, mineral, taninos finos.", "Cordero, setas"),
    "cyl_vita_tor_o": w("Vita Toro", "Bodegas y Viñedos", "Toro", "tinto", 86, "8-14€", "Toro de entrada en retail.", "Fruta madura, taninos directos.", "Pizza, empanada"),
    "cyl_divina_proporcion": w("Divina Proporción", "Bodegas Divina Proporción", "Toro", "tinto", 88, "14-24€", "Toro con nombre evocador; buena RCP.", "Ciruela negra, especias.", "Carne a la piedra"),
    "cyl_rejon_amarguillo": w("Rejón de Amarguillo", "Bodegas Rejón", "Toro", "tinto", 85, "8-14€", "Toro popular de zona de Morales.", "Fruta roja, taninos vivos.", "Cocido, fabada"),
    "cyl_numanthia_termes": w("Termes", "Numanthia-Termes", "Toro", "tinto", 89, "22-38€", "Segunda línea del grupo Numanthia; estructura.", "Mora, tabaco, elegancia.", "Asado, queso"),
    "cyl_pintia": w("Pintia", "Vega Sicilia", "Toro", "tinto", 94, "55-95€", "Hermano de Vega en Toro; potencia fina.", "Fruta negra, grafito, guarda.", "Vacío, caza mayor"),
    "cyl_dominio_bendito": w("Dominio del Bendito", "Dominio del Bendito", "Toro", "tinto", 90, "25-45€", "Toro de parcelas; estilo serio.", "Fruta negra, mineral, taninos pulidos.", "Cordero, setas"),
    # —— Bierzo ——
    "cyl_descendientes_jpalacios": w("Descendientes de J. Palacios Petalos", "Descendientes de J. Palacios", "Bierzo", "tinto", 90, "14-24€", "Mencía de entrada del sobrino de Álvaro Palacios; muy difundido.", "Floral, fruta roja, especias.", "Pulpo, setas, cerdo"),
    "cyl_godelia_mencia": w("Godelia Mencía", "Bodegas Godelia", "Bierzo", "tinto", 88, "12-22€", "Referente moderno del Bierzo.", "Frambuesa, violeta, mineral.", "Cordero, empanada gallega"),
    "cyl_pittacum_mencia": w("Pittacum", "Bodegas Pittacum", "Bierzo", "tinto", 87, "10-18€", "Mencía afrutada de Arganza.", "Cereza, especias dulces.", "Chorizo, pizza"),
    "cyl_dominio_tares": w("Dominio de Tares", "Dominio de Tares", "Bierzo", "tinto", 88, "14-24€", "Bodega estable en el valle del Bierzo.", "Fruta roja, humo suave.", "Fabada, carne"),
    "cyl_luna_beberide_mencia": w("Luna Beberide Mencía", "Luna Beberide", "Bierzo", "tinto", 86, "9-16€", "Mencía de consumo frecuente.", "Fruta roja directa.", "Tapeo"),
    "cyl_estefania_tilenus": w("Tilenus Crianza", "Bodegas Estefanía", "Bierzo", "tinto", 89, "16-28€", "Dehesa de los Romanos; Mencía estructurada.", "Mora, regaliz, roble.", "Cordero, setas"),
    "cyl_casar_burbia_mencia": w("Casar de Burbia Mencía", "Casar de Burbia", "Bierzo", "tinto", 88, "14-24€", "Ponferrada; Mencía de montaña.", "Fruta roja, mineral.", "Cecina, queso"),
    "cyl_valtuille_pago": w("Valtuille", "Castro Ventosa", "Bierzo", "tinto", 91, "28-48€", "Parcelas de Valtuille de Arriba; Mencía de guarda.", "Floral, fruta negra, elegancia.", "Caza menor, setas"),
    "cyl_peique_mencia": w("Peique", "Bodegas Peique", "Bierzo", "tinto", 87, "10-18€", "Villafranca; mencía popular.", "Cereza, especias.", "Embutido"),
    "cyl_nano_infante_mencia": w("Nano de Infesta Mencía", "Pequeños viticultores Bierzo", "Bierzo", "tinto", 86, "12-20€", "Estilo artesano de viñedo pequeño.", "Fruta roja, tierra.", "Cocido montañés"),
    "cyl_libamus_bierzo": w("Libamus", "Bodegas Libamus", "Bierzo", "tinto", 85, "8-14€", "Mencía de entrada.", "Fruta simple.", "Menú"),
    "cyl_mencia_robustiano": w("Robustiano Mencía", "Cooperativa Villafranca (referencia)", "Bierzo", "tinto", 84, "7-12€", "Mencía de volumen en zona bierzana.", "Fruta roja ligera.", "Pulpo, cachelos"),
    "cyl_godello_bierzo": w("Godello Bierzo", "Varios", "Bierzo", "blanco", 87, "10-18€", "Blanco atlántico cada vez más plantado en CyL.", "Manzana, sal, frescor.", "Marisco, pescado"),
    # —— Cigales, Tierra de León, Arribes, VT ——
    "cyl_prado_rey_cigales": w("Prado Rey Crianza", "Prado Rey", "Cigales", "tinto", 87, "10-18€", "Referente de Cigales; Tinta del País con carácter.", "Fruta roja, especias.", "Lechazo, queso"),
    "cyl_finca_valdeolivos": w("Finca Valdeolivos", "Finca Valdeolivos", "Cigales", "tinto", 86, "9-15€", "Tinto rosado-clarete y tintos de la DO.", "Fruta fresca, taninos medios.", "Tapas, cordero"),
    "cyl_frutos_villar_cigales": w("Viña Magna", "Frutos Villar", "Cigales", "tinto", 85, "8-14€", "Línea comercial de la cooperativa histórica.", "Fruta roja, fácil.", "Pizza"),
    "cyl_altolandon_prieto": w("Altolandon Prieto Picudo", "Altolandon", "Tierra de León", "tinto", 88, "14-26€", "Variedad autóctona leonesa; vinos de altitud.", "Fruta roja, pimienta, frescura.", "Cecina, queso de Valdeón"),
    "cyl_losada_mencia_leon": w("Losada", "Bodegas Losada", "Bierzo", "tinto", 89, "18-32€", "Mencía estructurada desde el corazón del Bierzo.", "Mora, mineral, taninos finos.", "Cordero, setas"),
    "cyl_casar_burbia_albarin": w("Casar de Burbia Godello / blancos", "Casar de Burbia", "Bierzo", "blanco", 87, "12-22€", "Blancos de montaña bierzana.", "Cítricos, mineral.", "Pescado, marisco"),
    "cyl_el_hato_garabato": w("El Hato y el Garabato", "El Hato y el Garabato", "Arribes", "tinto", 88, "16-28€", "DO Arribes del Duero; Juan García y otras variedades raras.", "Fruta roja silvestre, especias.", "Cordero, setas, queso"),
    "cyl_vetus_ordo": w("Vetus Ordo", "Vetus Ordo", "Arribes", "tinto", 87, "14-24€", "Proyecto en terruño fronterizo.", "Fruta roja, mineral.", "Cecina, embutido"),
    "cyl_alonso_del_yerro": w("Alonso del Yerro", "Bodegas Alonso del Yerro", "Ribera del Duero", "tinto", 91, "28-48€", "Proyecto de Jean Thienpont en la Ribera; estilo bordelés.", "Cassis, especias, taninos sedosos.", "Vaca, caza, quesos"),
    "cyl_abadia_retuerta_pago": w("Selección Especial Abadía Retuerta", "Abadía Retuerta", "V.T. Castilla y León", "tinto", 93, "45-85€", "Pago de Sardón de Duero; mezcla clásica bordalesa.", "Cassis, grafito, elegancia.", "Solomillo, quesos"),
    # —— +7 para completar 100 (Ribera / Rueda / Cigales) ——
    "cyl_valdrinal_crianza": w("Valdrinal Crianza", "Bodegas Valdrinal", "Ribera del Duero", "tinto", 86, "10-18€", "Ribera de Gumiel de Mercado; presencia en retail.", "Fruta roja, especias suaves.", "Cocido, embutido"),
    "cyl_vinas_jaro": w("Viñas del Jaro", "Viñas del Jaro", "Ribera del Duero", "tinto", 87, "12-20€", "Proyecto de La Horra; estilo clásico.", "Ciruela, vainilla ligera.", "Cordero, pasta"),
    "cyl_pradorey_verdejo": w("Prado Rey Verdejo", "Prado Rey", "Rueda", "blanco", 87, "8-14€", "Blanco de la bodega de Cigales con viñedo en Rueda.", "Hierbas, cítricos.", "Pescado, ensalada"),
    "cyl_bodegas_isla_cigales": w("Isla de Cigales", "Bodegas Isla", "Cigales", "tinto", 85, "8-14€", "Tinto accesible de la DO Cigales.", "Fruta roja, taninos ligeros.", "Tapas, pizza"),
    "cyl_emilio_moro_la_horra": w("La Horra", "Emilio Moro (viñedo La Horra)", "Ribera del Duero", "tinto", 91, "35-55€", "Selección de viñedo histórico de Moro en La Horra.", "Fruta negra densa, mineral, largo.", "Chuletón, quesos"),
    "cyl_finca_torremilanos": w("Torremilanos Crianza", "Finca Torremilanos", "Ribera del Duero", "tinto", 88, "14-24€", "Aranda de Duero; bodega con larga tradición.", "Fruta negra, roble equilibrado.", "Lechazo, guisos"),
    "cyl_dominio_del_pidio": w("Dominio del Pidio", "Dominio del Pidio", "Ribera del Duero", "tinto", 90, "22-40€", "Pequeño productor de Gumiel de Izán; Ribera artesanal.", "Fruta roja, especias, elegancia.", "Cordero, setas"),
}


def main() -> None:
    if len(NUEVOS) != 100:
        raise SystemExit(f"Se esperaban 100 entradas, hay {len(NUEVOS)}")
    data = json.loads(ESPANA.read_text(encoding="utf-8"))
    colisiones = [k for k in NUEVOS if k in data]
    if colisiones:
        raise SystemExit(f"Claves ya existentes en espana.json: {colisiones}")
    data.update(NUEVOS)
    ESPANA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: +{len(NUEVOS)} vinos CyL en espana.json (total claves: {len(data)})")


if __name__ == "__main__":
    main()
