"""Compila e importa todos los DAGs sin ejecutar las tareas ni acceder a GCP."""
import ast
import os
from pathlib import Path
import re
import sys
import tempfile

def main():
    root = Path(__file__).resolve().parents[1]
    os.environ.setdefault("AIRFLOW_HOME", tempfile.mkdtemp(prefix="ss2-airflow-"))
    os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
    from airflow.models import DagBag

    paths = sorted((root / "dags").glob("*.py"))
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bag = DagBag(dag_folder=str(root / "dags"), include_examples=False, safe_mode=False)
    errors = dict(bag.import_errors)
    for path in paths:
        dags = [dag for dag in bag.dags.values() if Path(dag.fileloc).resolve() == path.resolve()]
        if not dags:
            errors[str(path)] = "El archivo no publica ningun DAG"
        if not path.name.startswith("s8_"):
            match = re.fullmatch(r"([0-9]+)_[a-z0-9_]+\.py", path.name)
            if not match:
                errors[str(path)] = "Usar dags/<carnet numerico>_<nombre>.py"
            elif any(not dag.dag_id.startswith(f"estudiante_{match[1]}_") for dag in dags):
                errors[str(path)] = "El dag_id debe comenzar con estudiante_<carnet>_"
            for dag in dags:
                if dag.catchup or dag.max_active_runs != 1 or dag.schedule is not None:
                    errors[str(path)] = "DAG estudiantil: schedule=None, catchup=False, max_active_runs=1"
    if errors:
        for name, error in errors.items():
            print(f"ERROR {name}:\n{error}", file=sys.stderr)
        raise SystemExit(1)
    for dag in sorted(bag.dags.values(), key=lambda item: item.dag_id):
        print(f"OK {dag.dag_id}: {len(dag.tasks)} tareas")
    print(f"Validacion correcta: {len(bag.dags)} DAGs")

if __name__ == "__main__":
    main()
