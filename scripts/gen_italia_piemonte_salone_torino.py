# -*- coding: utf-8 -*-
"""
Genera data/italia_piemonte_salone_torino.json a partir del listado del Salone del Vino Torino.
Incluye bodegas / aziende agricole / cantine (excluye consorzi puramente institucionales, stands no vitivinícolas).
Ejecutar: python scripts/gen_italia_piemonte_salone_torino.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "italia_piemonte_salone_torino.json"

# (clave, bodega, municipio, sigla_provincia, tipo, nombre_vino_corto, nota_region)
# Siglas: TO Torino, CN Cuneo, AT Asti, AL Alessandria, NO Novara, BI Biella
RAW: list[tuple[str, str, str, str, str, str, str]] = [
    ("sdt_alle_tre_colline", "Alle Tre Colline", "Albugnano", "AT", "tinto", "Vino rosso Monferrato", "Colline Alfieri / Asti"),
    ("sdt_pianfiorito", "Pianfiorito", "Albugnano", "AT", "tinto", "Vino rosso Piemonte", "Albugnano"),
    ("sdt_terre_dei_santi", "Terre dei Santi", "Castelnuovo Don Bosco", "AT", "tinto", "Barbera o rosso locale", "Alto Monferrato astigiano"),
    ("sdt_mauro_vini", "Mauro Vini", "Dronero", "CN", "tinto", "Valli occidentali / rosso", "Valle Maira area"),
    ("sdt_ca_d_tantin", "Ca' d'Tantin", "Calosso", "AT", "tinto", "Calosso DOC / rosso", "Calosso"),
    ("sdt_maggiora", "Az. Agr. Maggiora", "Refrancore", "AT", "tinto", "Monferrato rosso", "Refrancore"),
    ("sdt_carussin", "Carussin", "San Marzano Oliveto", "AT", "tinto", "Barbera d'Asti", "Nizza terroir cercano"),
    ("sdt_fam_silano_refrancore", "Fam. Silano Refrancore", "Agliano Terme", "AT", "tinto", "Barbera d'Asti", "Agliano"),
    ("sdt_auriel", "Auriel", "Moncalvo", "AT", "tinto", "Grignolino o Barbera", "Moncalvo"),
    ("sdt_adriano_grasso", "Adriano Grasso", "Calosso", "AT", "tinto", "Calosso / rosso", "Calosso"),
    ("sdt_rovero", "Rovero", "San Marzano Oliveto", "AT", "tinto", "Barbera", "Alto Monferrato"),
    ("sdt_torelli", "Torelli", "Bubbio", "AT", "tinto", "Moscato o rosso locale", "Bubbio"),
    ("sdt_bruno_franco", "Bruno Franco", "Isola d'Asti", "AT", "tinto", "Barbera d'Asti", "Isola d'Asti"),
    ("sdt_az_stra", "Az. Agr. Stra", "Novello", "CN", "tinto", "Langhe Dolcetto", "Novello Langhe"),
    ("sdt_issardi_ernesto", "Az. Agr. Issardi Ernesto", "Castagnito", "CN", "tinto", "Langhe rosso", "Roero / Langhe"),
    ("sdt_antica_cascina_san_rocco", "Antica Cascina San Rocco", "Ricaldone", "AL", "tinto", "Monferrato rosso", "Alto Monferrato alessandrino"),
    ("sdt_daniele_guglielmi", "Daniele Guglielmi", "Canelli", "AT", "blanco", "Moscato / Cortese", "Canelli"),
    ("sdt_rabino_luigi", "Az. Agr. Rabino Luigi Giuseppe", "Canale", "CN", "tinto", "Roero / Nebbiolo", "Canale Roero"),
    ("sdt_torraccia_piantavigna", "Torraccia del Piantavigna", "Ghemme", "NO", "tinto", "Ghemme DOCG Nebbiolo", "Alto Piemonte"),
    ("sdt_ii_masot_montanaro", "Az. Agr. II Masot di Montanaro Andrea", "Santo Stefano Belbo", "CN", "blanco", "Moscato d'Asti / Langhe", "Langhe"),
    ("sdt_venturino_ezio", "Venturino Ezio", "Vigliano d'Asti", "AT", "tinto", "Barbera d'Asti", "Vigliano"),
    ("sdt_erbaluna", "Az. Agr. Erbaluna", "La Morra", "CN", "tinto", "Langhe Nebbiolo / Barolo", "La Morra Langhe"),
    ("sdt_cascina_preghiera", "Cascina Preghiera", "Castellengo di Cossato", "BI", "tinto", "Lessona / rosso", "Biella viticoltura"),
    ("sdt_pietro_cassina", "Pietro Cassina", "Lessona", "BI", "tinto", "Lessona DOC", "Alto Piemonte Biellese"),
    ("sdt_donatella_pelodi", "Donatella", "Pelodi Ligure", "AL", "tinto", "Ovada / rosso", "Appennino alessandrino"),
    ("sdt_padrin", "Padrin", "Mornese", "AL", "tinto", "Cortese o rosso Colli", "Mornese"),
    ("sdt_boffa_fratelli", "Az. Agr. Boffa Fratelli", "Diano d'Alba", "CN", "tinto", "Dolcetto d'Alba", "Langhe"),
    ("sdt_ii_palazzotto", "Az. Agr. II Palazzotto", "Diano d'Alba", "CN", "tinto", "Dolcetto d'Alba", "Diano"),
    ("sdt_montalegre", "Az. Agr. Montalegre", "Tortona", "AL", "blanco", "Timorasso Derthona", "Colli Tortonesi"),
    ("sdt_la_voltignana", "La Voltignana", "Mornese", "AL", "tinto", "Rosso Monferrato", "Mornese"),
    ("sdt_flavio_baudana", "Az. Agr. Flavio Baudana", "Serralunga d'Alba", "CN", "tinto", "Barolo", "Serralunga"),
    ("sdt_villa_felice", "Villa Felice", "Cassine", "AL", "tinto", "Dolcetto o Barbera", "Cassine"),
    ("sdt_tenuta_roletto", "Tenuta Roletto", "Cuceglio", "TO", "tinto", "Canavese rosso", "Torino collina"),
    ("sdt_cantina_sette", "Cantina Sette", "Govone", "CN", "tinto", "Roero / Barbera", "Govone"),
    ("sdt_bosco_canale", "Bosco", "Canale", "AT", "tinto", "Barbera", "Canale Roero"),
    ("sdt_tenuta_monferrato_coop", "Tenuta Monferrato Soc. Agr. Coop.", "Clavesana", "CN", "tinto", "Langhe rosso", "Alta Langa area"),
    ("sdt_cantina_nizza_savia", "Cantina di Nizza Sotto la Savia", "Incisa Scapaccino", "AT", "tinto", "Barbera d'Asti Superiore", "Nizza DOCG zona"),
    ("sdt_cascina_garitina", "Cascina Garitina", "Castelnuovo Calcea", "AT", "tinto", "Barbera d'Asti", "Calcea"),
    ("sdt_scarzella", "Scarzella", "Castagnito", "CN", "tinto", "Langhe rosso", "Roero"),
    ("sdt_alvio_pestarino", "Alvio Pestarino", "Capriata d'Orba", "AL", "tinto", "Gavi o Barbera", "Alto Monferrato"),
    ("sdt_cantina_biscotto", "Cantina Biscotto", "Carpineto", "AL", "tinto", "Monferrato casalese", "Carpineto"),
    ("sdt_cascina_alma", "Cascina Alma", "Cassine", "AL", "tinto", "Dolcetto", "Cassine"),
    ("sdt_castello_grillano", "Castello di Grillano", "Ovada", "AL", "tinto", "Ovada DOCG Dolcetto", "Ovada"),
    ("sdt_facchino_vini", "Facchino Vini", "Rocca Grimalda", "AL", "tinto", "Cortese / rosso", "Ovada area"),
    ("sdt_la_valletta", "La Valletta", "Cremolino", "AL", "tinto", "Dolcetto Ovada", "Cremolino"),
    ("sdt_paschetta_vini", "Paschetta Vini", "Carpineto", "AL", "tinto", "Monferrato", "Carpineto"),
    ("sdt_rocca_rondinaria", "Rocca Rondinaria", "Rocca Grimalda", "AL", "tinto", "Rosso locale", "Alto Monferrato"),
    ("sdt_rossi_di_nuovo", "Rossi di Nuovo", "Rocca Grimalda", "AL", "tinto", "Barbera / Dolcetto", "Rocca Grimalda"),
    ("sdt_valletta_carpineto", "Valletta", "Carpineto", "AL", "tinto", "Monferrato rosso", "Carpineto"),
    ("sdt_tre_secoli", "Tre secoli", "Mombaruzzo", "AT", "tinto", "Barbera d'Asti", "Mombaruzzo"),
    ("sdt_cantina_casorzo", "Cantina Sociale di Casorzo", "Casorzo", "AT", "rosado", "Malvasia di Casorzo", "Casorzo"),
    ("sdt_taverna_nieve", "Taverna", "Neive", "CN", "tinto", "Barbaresco / Dolcetto", "Langhe Neive"),
    ("sdt_amelio_livio", "Az. Agr. Amelio Livio", "Grana", "AT", "tinto", "Monferrato", "Grana Monferrato"),
    ("sdt_cascina_ciuche", "Cascina Ciuché", "Castiglione d'Asti", "AT", "tinto", "Barbera", "Castiglione"),
    ("sdt_amerio_vincenzo", "Az. Agr. Amerio Vincenzo", "Moasca", "AT", "tinto", "Barbera d'Asti", "Moasca"),
    ("sdt_ferro_carlo_figli", "Ferro Carlo e figli", "Castiglione d'Asti", "AT", "tinto", "Barbera", "Castiglione"),
    ("sdt_filippa_agliano", "Az. Agr. Filippa", "Agliano Terme", "AT", "tinto", "Barbera d'Asti", "Agliano"),
    ("sdt_soc_agricola_b8", "Società Agricola B8", "Ricaldone", "AL", "tinto", "Monferrato", "Ricaldone"),
    ("sdt_vaudano_enrico", "Vaudano Enrico e figli", "Cisterna d'Asti", "AT", "tinto", "Barbera", "Cisterna"),
    ("sdt_santanna_bricchetti", "Sant'Anna dei Bricchetti", "Costigliole d'Asti", "AT", "tinto", "Barbera d'Asti Superiore", "Nizza terroir"),
    ("sdt_bianco_marco", "Bianco Marco", "Costigliole d'Asti", "AT", "tinto", "Barbera", "Costigliole"),
    ("sdt_prediomagno", "Prediomagno", "Grana Monferrato", "AT", "tinto", "Barbera", "Grana"),
    ("sdt_cascina_ghercina", "Cascina Ghercina", "Nizza Monferrato", "AT", "tinto", "Barbera d'Asti Superiore Nizza", "Nizza DOCG"),
    ("sdt_cascina_corsico", "Cascina Corsico", "Vigliano d'Asti", "AT", "tinto", "Barbera", "Vigliano"),
    ("sdt_cascina_meilogis", "Cascina Meilogis", "Revello", "CN", "tinto", "Langhe rosso", "Revello"),
    ("sdt_poderi_moretti", "Poderi Moretti", "Monteu Roero", "CN", "tinto", "Roero Arneis / rosso", "Roero"),
    ("sdt_roggero_albugnano", "Roggero", "Albugnano", "AT", "tinto", "Barbera", "Albugnano"),
    ("sdt_drocco_renzo", "Drocco Renzo", "Rodello", "CN", "tinto", "Langhe Dolcetto", "Rodello"),
    ("sdt_la_tribulera", "La Tribulera", "Santo Stefano Belbo", "CN", "blanco", "Moscato / Langhe", "Belbo"),
    ("sdt_cascina_del_pozzo", "Cascina del Pozzo", "Castellinaldo d'Alba", "TO", "tinto", "Canavese / rosso", "Castellinaldo"),
    ("sdt_barisone_simone_gavi", "Az. Agr. Barisone Simone", "Gavi", "AL", "blanco", "Gavi di Gavi DOCG", "Gavi"),
    ("sdt_rigo_silvano", "Rigo Silvano", "Alba", "CN", "tinto", "Langhe Nebbiolo / Dolcetto", "Alba"),
    ("sdt_costa_gatterina", "Costa Gatterina", "Castagnito", "CN", "tinto", "Roero", "Castagnito"),
    ("sdt_ferro_fratelli_tinella", "Ferro Fratelli", "Castiglione Tinella", "CN", "blanco", "Moscato d'Asti", "Tinella"),
    ("sdt_az_bosco_lanze", "Az. Agr. Bosco", "Castagnole delle Lanze", "AT", "tinto", "Barbera d'Asti", "Nizza zona"),
    ("sdt_torchietto", "Torchietto", "Isola d'Asti", "AT", "tinto", "Barbera", "Isola d'Asti"),
    ("sdt_crosio", "Crosio", "Candia Canavese", "TO", "tinto", "Canavese rosso", "Canavese"),
    ("sdt_carlin_de_paolo", "Carlin de Paolo", "San Damiano d'Asti", "AT", "tinto", "Barbera", "San Damiano"),
    ("sdt_cantina_vinchio_vaglio", "Cantina Sociale di Vinchio Vaglio", "Vinchio", "AT", "tinto", "Barbera d'Asti", "Nizza"),
    ("sdt_vigne_dei_mastri", "Vigne dei Mastri", "Costigliole d'Asti", "AT", "tinto", "Barbera", "Costigliole"),
    ("sdt_cantina_vida", "Cantina VIDA", "Mongardino", "AT", "tinto", "Barbera", "Mongardino"),
    ("sdt_la_rachilana", "La Rachilana", "Monforte d'Alba", "CN", "tinto", "Barolo / Langhe", "Monforte"),
    ("sdt_savigliano_fratelli", "Savigliano Fratelli", "Diano d'Alba", "CN", "tinto", "Dolcetto d'Alba", "Diano"),
    ("sdt_casavecchia_diano", "Az. Agr. Casavecchia", "Diano d'Alba", "CN", "tinto", "Dolcetto d'Alba", "Diano"),
    ("sdt_cascina_saria", "Cascina Saria", "Neive", "CN", "tinto", "Barbaresco / Dolcetto", "Neive"),
    ("sdt_vermouth_anselmo", "Vermouth Anselmo", "Torino", "TO", "blanco", "Vermouth di Torino", "Tradizione torinese"),
    ("sdt_san_biagio_roggero", "Az. Agr. San Biagio di Roggero C.", "La Morra", "CN", "tinto", "Barolo / Langhe", "La Morra"),
    ("sdt_tenuta_genovilla", "Tenuta Genovilla", "Ozzano Monferrato", "AL", "tinto", "Grignolino / Barbera", "Monferrato"),
    ("sdt_tenuta_san_bernardo", "Tenuta San Bernardo", "Vigliano d'Asti", "AT", "tinto", "Barbera", "Vigliano"),
    ("sdt_pierino_vellano", "Cantina Pierino Vellano Cà San Sebastiano", "Camino", "AL", "tinto", "Monferrato casalese", "Camino"),
    ("sdt_danilo_spinoglio", "Danilo Spinoglio", "Sala Monferrato", "AL", "tinto", "Grignolino", "Sala Monferrato"),
    ("sdt_castello_gabiano", "Castello di Gabiano", "Gabiano", "AL", "tinto", "Gabiano DOC", "Monferrato"),
    ("sdt_tenaglia", "Az. Agr. Tenaglia", "Serralunga di Crea", "AL", "tinto", "Monferrato", "Crea"),
    ("sdt_coppo_giovanni", "Az. Agr. Coppo Giovanni", "Cella Monte", "AL", "blanco", "Timorasso / Cortese", "Cella Monte"),
    ("sdt_la_vignazza_cossotto", "La Vignazza di Cossotto Arturo", "Alfiano Natta", "AL", "tinto", "Monferrato", "Alfiano"),
    ("sdt_tenuta_ca_duat", "Tenuta Cà Duat", "Vignale Monferrato", "AL", "tinto", "Barbera del Monferrato", "Vignale"),
    ("sdt_podere_il_gelsi", "Podere il Gelsi", "Casal Cermelli", "AL", "tinto", "Rosso Monferrato", "Alessandrino"),
    ("sdt_alemat", "Alemat", "Ponzano Monferrato", "AL", "tinto", "Barbera", "Ponzano"),
    ("sdt_hic_et_nunc", "Hic et nunc", "Vignale Monferrato", "AL", "tinto", "Barbera", "Vignale"),
    ("sdt_cinque_quinti", "Cinque Quinti", "Cella Monte", "AL", "blanco", "Timorasso", "Cella Monte"),
    ("sdt_san_pietro_vignale", "San Pietro", "Vignale Monferrato", "AL", "tinto", "Barbera", "Vignale"),
    ("sdt_gavi_giovani", "Gavi Giovani", "Gavi", "AL", "blanco", "Gavi DOCG", "Gavi"),
    ("sdt_fontanafredda_salone", "Fontanafredda", "Serralunga d'Alba", "CN", "tinto", "Barolo / Langhe", "Grupo histórico Langhe"),
    ("sdt_valle_asinari", "Valle Asinari", "Barolo", "CN", "tinto", "Barolo", "Barolo"),
    ("sdt_mascarello_m", "Cantina Mascarello M.", "La Morra", "CN", "tinto", "Barolo", "La Morra"),
    ("sdt_ramello_gianfranco", "Ramello Gianfranco e Matteo", "La Morra", "CN", "tinto", "Barolo / Langhe", "La Morra"),
    ("sdt_castello_azeglio", "Castello di Azeglio", "Azeglio", "TO", "tinto", "Canavese / Erbaluce", "Canavese"),
    ("sdt_cantina_carema", "Cantina dei Produttori di Carema", "Carema", "TO", "tinto", "Carema DOC Nebbiolo", "Canavese"),
    ("sdt_giro_di_vite", "Giro di Vite", "Pinerolo", "TO", "tinto", "Pinerolese DOC", "Pinerolese"),
    ("sdt_la_palera", "La Palera", "Borgomasino", "TO", "tinto", "Canavese", "Borgomasino"),
    ("sdt_galindro_serra", "Galindro della Serra", "Piverone", "TO", "tinto", "Canavese rosso", "Piverone"),
    ("sdt_lautin_barge", "L'Autin", "Barge", "CN", "tinto", "Colline Saluzzesi", "Valle Po"),
    ("sdt_fratelli_marco_loranzè", "Fratelli Marco - Vignaioli Cantunieri", "Loranzè", "TO", "tinto", "Canavese Erbaluce", "Loranzè"),
    ("sdt_le_marie", "Le Marie", "Barge", "CN", "tinto", "Rosso Piemonte", "Barge"),
    ("sdt_stefano_rossotto", "Az. Agr. Stefano Rossotto", "Cinzano", "TO", "tinto", "Canavese", "Cinzano"),
    ("sdt_luca_leggero", "Luca Leggero", "Carmagnola", "TO", "tinto", "Pinerolese / locale", "Carmagnola"),
    ("sdt_poderi_roccanera", "Poderi Roccanera", "Cossano Belbo", "CN", "blanco", "Moscato / Langhe", "Belbo"),
    ("sdt_tojo", "Tojo", "Santo Stefano Belbo", "CN", "blanco", "Moscato d'Asti", "Belbo"),
    ("sdt_balbiano", "Balbiano", "Pino Torinese", "TO", "tinto", "Canavese", "Collina torinese"),
    ("sdt_terrenostre", "Terrenostre", "Cossano Belbo", "CN", "tinto", "Langhe rosso", "Belbo"),
    ("sdt_criolin", "Criolin Az. Agr.", "Castagnole delle Lanze", "AT", "tinto", "Barbera d'Asti", "Nizza zona"),
    ("sdt_canaparo_roberto", "Az. Agr. Canaparo Roberto", "Santo Stefano Belbo", "CN", "blanco", "Moscato", "Belbo"),
    ("sdt_viberti", "Az. Agr. Viberti", "Barolo", "CN", "tinto", "Barolo", "Barolo"),
    ("sdt_az_vitivinicola_piano", "Az. Agr. Vitivinicola Piano", "Calosso", "AT", "tinto", "Calosso / Barbera", "Calosso"),
    ("sdt_cantina_tortona", "Cantina di Tortona", "Tortona", "AL", "blanco", "Timorasso Colli Tortonesi", "Tortona"),
    ("sdt_ca_bianca_loazzolo", "Ca' Bianca", "Loazzolo", "AT", "blanco", "Moscato passito Loazzolo", "Loazzolo"),
    ("sdt_bossotti", "Az. Agr. Vincenzo Bossotti", "Cisterna d'Asti", "AT", "tinto", "Barbera", "Cisterna"),
    ("sdt_barbera_sei_castelli", "Cantina Sociale Barbera dei Sei Castelli", "Agliano Terme", "AT", "tinto", "Barbera d'Asti", "Nizza"),
    ("sdt_la_canellese", "Az. Agr. La Canellese di Sacco", "Agliano Terme", "AT", "tinto", "Barbera", "Agliano"),
    ("sdt_uvamatris", "Uvamatris", "Sala Monferrato", "AL", "tinto", "Grignolino", "Sala"),
    ("sdt_araldica_castelvero", "Araldica Castelvero", "Castel Boglione", "AT", "tinto", "Barbera d'Asti", "Nizza Monferrato"),
    ("sdt_ugo_balocco", "Ugo Balocco", "San Marzano Oliveto", "AT", "tinto", "Barbera", "San Marzano"),
]


def slug_conflict_check(keys: list[str]) -> None:
    seen: set[str] = set()
    for k in keys:
        if k in seen:
            raise ValueError(f"Duplicate key {k}")
        seen.add(k)


def main() -> None:
    slug_conflict_check([r[0] for r in RAW])
    out: dict[str, dict] = {}
    for key, bodega, comune, prov, tipo, nombre, subz in RAW:
        region = f"Piamonte, {subz} ({prov})"
        desc = (
            f"Productor presente en el Salone del Vino Torino; sede en {comune} "
            f"(provincia {prov}). Referencia vitivinícola del Piemonte."
        )
        out[key] = {
            "nombre": nombre,
            "bodega": bodega,
            "region": region,
            "pais": "Italia",
            "tipo": tipo,
            "puntuacion": 86,
            "precio_estimado": "12-35€",
            "descripcion": desc,
            "notas_cata": "Notas típicas de la zona: fruta roja, especias suaves, acidez viva en blancos aromáticos.",
            "maridaje": "Cocina piemontesa, tajarin, quesos, trufa en tintos estructurados.",
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(out)} bodegas/productores -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
