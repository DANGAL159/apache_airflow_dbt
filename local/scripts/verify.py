"""docker compose exec airflow-scheduler python /opt/airflow/local/verify.py start|status"""
from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import sys

import psycopg2
import requests

BASE = "http://airflow-api-server:8080"
STATE = Path("/opt/airflow/logs/verificacion_local.json")

def main():
    session = requests.Session()
    response = session.post(BASE + "/auth/token", json={"username": "admin", "password": "admin"}, timeout=30)
    response.raise_for_status()
    session.headers["Authorization"] = "Bearer " + response.json()["access_token"]
    def call(method, path, data=None):
        response = session.request(method, BASE + "/api/v2" + path, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    if sys.argv[1] == "start":
        if STATE.exists():
            raise RuntimeError("Ya existe una verificacion. Usar status para consultar sus resultados.")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        state = {"started_at": stamp, "cases": []}
        cases = [
            ("s8_saludo", "saludo", {}, "success"),
            ("s8_ventas", "etl", {}, "success"),
            ("s8_sql_idempotente", "sql", {}, "success"),
            ("s8_dbt_sgfood", "dbt", {}, "success"),
            ("estudiante_202600001_dbt", "estudiante", {}, "success"),
            ("estudiante_202600001_dbt", "repeticion", {}, "success"),
            ("s8_fallos_controlados", "reintento", {"fallo_transitorio": True}, "success"),
            ("s8_fallos_controlados", "calidad", {"dato_invalido": True}, "failed"),
            ("s8_fallos_controlados", "recuperacion", {}, "success"),
        ]
        for dag, name, conf, expected in cases:
            call("PATCH", f"/dags/{dag}", {"is_paused": False})
            run = f"local_{stamp}_{name}"
            call("POST", f"/dags/{dag}/dagRuns", {"dag_run_id": run, "logical_date": None, "conf": conf})
            state["cases"].append({"dag": dag, "run": run, "expected": expected})
            STATE.write_text(json.dumps(state, indent=2))
        print("Nueve ejecuciones de prueba creadas")
        return
    state = json.loads(STATE.read_text())
    complete = True
    for case in state["cases"]:
        run = call("GET", f"/dags/{case['dag']}/dagRuns/{case['run']}")
        case["state"] = run["state"]
        tasks = call("GET", f"/dags/{case['dag']}/dagRuns/{case['run']}/taskInstances")
        case["tasks"] = [{k: t.get(k) for k in ("task_id", "state", "try_number")} for t in tasks["task_instances"]]
        complete = complete and case["state"] == case["expected"]
        print(case["run"], case["state"])
    if complete:
        state["warehouse"] = {}
        with psycopg2.connect(host="warehouse", user="sgfood", password=os.environ["DBT_PASSWORD"], dbname="sgfood_dw") as conn:
            with conn.cursor() as cursor:
                for schema, folder in (("analytics", "docente"), ("alumno_202600001", "202600001")):
                    cursor.execute(f"SELECT COUNT(*), COUNT(DISTINCT venta_id), SUM(monto_neto) FROM {schema}_marts.fact_ventas")
                    count, unique, total = cursor.fetchone()
                    assert count == unique == 10 and total == Decimal("3766.75")
                    results = json.loads(Path(f"/opt/airflow/logs/dbt/{folder}/target/run_results.json").read_text())["results"]
                    assert all(r["status"] in ("pass", "success") for r in results)
                    tests = sum(r["unique_id"].startswith("test.") for r in results)
                    assert tests == 38
                    state["warehouse"][schema] = {"ventas": count, "unicas": unique, "total": str(total), "pruebas_dbt": tests}
                cursor.execute("SELECT COUNT(*), SUM(total) FROM raw.ventas WHERE venta_id=1")
                assert cursor.fetchone() == (1, Decimal("50.00"))
        files = list(Path("/opt/airflow/logs/s8_resultados").glob("*.json"))
        assert files
        for file in files:
            data = json.loads(file.read_text())
            assert len(data) == 3 and sum(Decimal(row["total"]) for row in data) == Decimal("95.00")
        retry = next(c for c in state["cases"] if c["run"].endswith("_reintento"))
        assert next(t for t in retry["tasks"] if t["task_id"] == "extraer")["try_number"] == 2
        failure = next(c for c in state["cases"] if c["expected"] == "failed")
        assert next(t for t in failure["tasks"] if t["task_id"] == "publicar")["state"] == "upstream_failed"
        state["verified_at"] = datetime.now(timezone.utc).isoformat()
    state["all_expected"] = complete
    STATE.write_text(json.dumps(state, indent=2))
    print("Verificacion completa:", complete)
    if complete:
        print(json.dumps(state["warehouse"], indent=2))

if __name__ == "__main__":
    main()
