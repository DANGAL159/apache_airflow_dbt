#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check \
  -r requirements-dev.txt \
  --constraint https://raw.githubusercontent.com/apache/airflow/constraints-3.1.1/constraints-3.12.txt
printf '\nEntorno listo. Ejecuta:\n  source .venv/bin/activate\n  python scripts/crear_dag.py TU_CARNET\n  python scripts/validar_dags.py\n'
