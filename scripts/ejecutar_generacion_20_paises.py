"""
Ejecuta la generacion masiva de vinos por pais (500 por pais, 20 paises).
Requisitos: OPENROUTER_API_KEY o OPENAI_API_KEY en .env
Uso:
  python scripts/ejecutar_generacion_20_paises.py              # todos los paises
  python scripts/ejecutar_generacion_20_paises.py --pais francia  # solo Francia
  python scripts/ejecutar_generacion_20_paises.py --dry-run    # prueba 10 vinos por pais
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAISES_OUTPUT = [
    ("espana", "data/vinos_es_masivos.json"),
    ("francia", "data/vinos_fr_masivos.json"),
    ("italia", "data/vinos_it_masivos.json"),
    ("portugal", "data/vinos_pt_masivos.json"),
    ("alemania", "data/vinos_de_masivos.json"),
    ("argentina", "data/vinos_ar_masivos.json"),
    ("chile", "data/vinos_cl_masivos.json"),
    ("usa", "data/vinos_us_masivos.json"),
    ("australia", "data/vinos_au_masivos.json"),
    ("nueva_zelanda", "data/vinos_nz_masivos.json"),
    ("sudafrica", "data/vinos_za_masivos.json"),
    ("uruguay", "data/vinos_uy_masivos.json"),
    ("suiza", "data/vinos_ch_masivos.json"),
    ("austria", "data/vinos_at_masivos.json"),
    ("hungria", "data/vinos_hu_masivos.json"),
    ("grecia", "data/vinos_gr_masivos.json"),
    ("japon", "data/vinos_jp_masivos.json"),
    ("china", "data/vinos_cn_masivos.json"),
    ("brasil", "data/vinos_br_masivos.json"),
    ("colombia", "data/vinos_co_masivos.json"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pais", type=str, default="", help="Solo este pais (ej. francia)")
    parser.add_argument("--cantidad", type=int, default=500, help="Vinos por pais")
    parser.add_argument("--batch", type=int, default=50, help="Vinos por peticion IA")
    parser.add_argument("--dry-run", action="store_true", help="Prueba: 10 vinos por pais")
    args = parser.parse_args()

    if args.pais:
        paises = [(args.pais, next((o for p, o in PAISES_OUTPUT if p == args.pais), f"data/vinos_{args.pais}_masivos.json"))]
        if not any(p == args.pais for p, _ in PAISES_OUTPUT):
            print(f"Pais no valido. Opciones: {[p for p, _ in PAISES_OUTPUT]}")
            sys.exit(1)
    else:
        paises = PAISES_OUTPUT

    cantidad = 10 if args.dry_run else args.cantidad
    for pais, output in paises:
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "generar_vinos_ia.py"),
            "--pais", pais,
            "--cantidad", str(cantidad),
            "--batch", str(args.batch),
            "--output", output,
        ]
        if args.dry_run:
            cmd.append("--dry-run")
        print(f"\n>>> {pais} -> {output}")
        ret = subprocess.run(cmd, cwd=str(ROOT))
        if ret.returncode != 0:
            print(f"ERROR: generacion fallo para {pais}")
            sys.exit(ret.returncode)
    print("\nListo. Para unificar todos los JSON en uno, usa el backend: carga todos los data/*.json (excluye analytics, etc.).")


if __name__ == "__main__":
    main()
