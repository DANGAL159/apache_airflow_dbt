"""Pruebas reales del taller mediante HTTPS; lee credenciales del estado local.

Uso desde la raiz: python scripts/verificar_gcp.py start|status
No imprime ni guarda tokens o contrasenas.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".generated/pruebas_gcp.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "status"])
    args = parser.parse_args()
    outputs = json.loads(subprocess.check_output(["terraform", "-chdir=" + str(ROOT / "infra/terraform"), "output", "-json"], text=True))
    base = outputs["airflow_url"]["value"]
    def call(method, path, data=None, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        request = urllib.request.Request(base + path, data=None if data is None else json.dumps(data).encode(), headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=40) as response:
            return json.load(response)
    token = call("POST", "/auth/token", {"username": "admin", "password": outputs["admin_password"]["value"]})["access_token"]
    if args.action == "start":
        if STATE.exists():
            raise RuntimeError("Ya existe una prueba; usar status para conservar las ejecuciones")
        cases = [
            ("s8_saludo", "saludo", {}, "success"),
            ("s8_ventas", "etl", {}, "success"),
            ("s8_sql_idempotente", "sql", {}, "success"),
            ("s8_dbt_sgfood", "dbt", {}, "success"),
            ("estudiante_202600001_dbt", "estudiante", {}, "success"),
            ("s8_fallos_controlados", "reintento", {"fallo_transitorio": True}, "success"),
            ("s8_fallos_controlados", "calidad", {"dato_invalido": True}, "failed"),
            ("s8_fallos_controlados", "recuperacion", {}, "success"),
        ]
        state = {"url": base, "date": datetime.now(timezone.utc).isoformat(), "cases": []}
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        for dag, label, conf, expected in cases:
            call("PATCH", f"/api/v2/dags/{dag}", {"is_paused": False}, token)
            run = f"prueba_gcp_{stamp}_{label}"
            call("POST", f"/api/v2/dags/{dag}/dagRuns", {"dag_run_id": run, "logical_date": None, "conf": conf}, token)
            state["cases"].append({"dag": dag, "run": run, "expected": expected})
        STATE.parent.mkdir(exist_ok=True)
        STATE.write_text(json.dumps(state, indent=2))
        print("Ocho ejecuciones creadas en GCP")
        return
    state = json.loads(STATE.read_text())
    ok = True
    for case in state["cases"]:
        case["state"] = call("GET", f"/api/v2/dags/{case['dag']}/dagRuns/{case['run']}", token=token)["state"]
        tasks = call("GET", f"/api/v2/dags/{case['dag']}/dagRuns/{case['run']}/taskInstances", token=token)
        case["tasks"] = [{k: t.get(k) for k in ("task_id", "state", "try_number")} for t in tasks["task_instances"]]
        ok = ok and case["state"] == case["expected"]
        print(case["dag"], case["run"], case["state"], case["tasks"])
    viewer = call("POST", "/auth/token", {"username": "estudiantes", "password": outputs["viewer_password"]["value"]})["access_token"]
    call("GET", "/api/v2/dags?limit=100", token=viewer)
    state["viewer_read_access"] = True
    try:
        call("PATCH", "/api/v2/dags/s8_saludo", {"is_paused": False}, viewer)
    except urllib.error.HTTPError as error:
        assert error.code == 403
        state["viewer_write_denied"] = True
    else:
        raise AssertionError("La cuenta de estudiantes no debe modificar DAGs")
    state["all_expected"] = ok
    STATE.write_text(json.dumps(state, indent=2))
    print("Todos los resultados esperados:", ok)

if __name__ == "__main__":
    main()
