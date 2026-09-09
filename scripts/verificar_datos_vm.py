"""Ejecutar con sudo python3 en la VM para conciliar el ejemplo docente y estudiantil."""
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import subprocess

ROOT = Path("/opt/ss2-airflow-dbt")
COMMAND = ["docker", "compose", "--env-file", str(ROOT / "runtime/.env"), "-f", str(ROOT / "runtime/docker-compose.yml")]

def main():
    results = {}
    for schema, folder in (("analytics", "docente"), ("alumno_202600001", "202600001")):
        sql = f"SELECT COUNT(*), COUNT(DISTINCT venta_id), SUM(monto_neto) FROM {schema}_marts.fact_ventas"
        text = subprocess.check_output(COMMAND + ["exec", "-T", "warehouse", "psql", "-U", "sgfood", "-d", "sgfood_dw", "-t", "-A", "-F", ",", "-c", sql], text=True).strip()
        count, unique, total = text.split(",")
        assert int(count) == int(unique) == 10 and Decimal(total) == Decimal("3766.75")
        dbt = json.loads((ROOT / f"logs/dbt/{folder}/target/run_results.json").read_text())["results"]
        assert len(dbt) == 52 and all(r["status"] in ("success", "pass") for r in dbt)
        tests = sum(r["unique_id"].startswith("test.") for r in dbt)
        assert tests == 38
        results[schema] = {"ventas": int(count), "ventas_unicas": int(unique), "total_neto": total, "pruebas_dbt": tests, "recursos_dbt": len(dbt)}
    sql = "SELECT COUNT(*), SUM(total) FROM raw.ventas WHERE venta_id=1"
    row = subprocess.check_output(COMMAND + ["exec", "-T", "warehouse", "psql", "-U", "sgfood", "-d", "sgfood_dw", "-t", "-A", "-F", ",", "-c", sql], text=True).strip()
    assert row == "1,50.00"
    outputs = list((ROOT / "logs/s8_resultados").glob("*.json"))
    assert outputs
    for output in outputs:
        data = json.loads(output.read_text())
        assert len(data) == 3 and sum(Decimal(r["total"]) for r in data) == Decimal("95.00")
    print(json.dumps({"verified_at": datetime.now(timezone.utc).isoformat(), "warehouse": results, "sql_idempotente": row, "etl_total": "95.00", "etl_filas": 3}, indent=2))

if __name__ == "__main__":
    main()
