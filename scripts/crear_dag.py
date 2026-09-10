"""Genera un DAG estudiantil con identificadores y esquema propios."""
import argparse
from pathlib import Path
import re

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("carnet", help="Carnet numerico de longitud variable")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]+", args.carnet):
        parser.error("El carnet debe contener uno o mas digitos (0-9)")
    root = Path(__file__).resolve().parents[1]
    target = root / "dags" / f"{args.carnet}_airflow_dbt.py"
    template = (root / "plantillas/estudiante_dbt.py.template").read_text(encoding="utf-8")
    with target.open("x", encoding="utf-8") as file:
        file.write(template.replace("__CARNET__", args.carnet))
    print(f"Creado: {target.relative_to(root)}")
    print(f"DAG: estudiante_{args.carnet}_dbt | esquema base: alumno_{args.carnet}")

if __name__ == "__main__":
    main()
