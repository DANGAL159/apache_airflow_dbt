from datetime import timedelta
import pendulum
from airflow.sdk import dag, task, get_current_context

@dag(
    dag_id="s8_ventas",
    schedule=None,
    start_date=pendulum.datetime(
        2026, 1, 1, tz="America/Guatemala"
    ),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(seconds=30),
        "execution_timeout": timedelta(minutes=5),
    },
    tags=["semana8", "sgfood"],
)
def ventas():
    @task
    def extraer():
        return [
            {"id": 1, "cantidad": 2, "precio": "25.00"},
            {"id": 2, "cantidad": 1, "precio": "30.00"},
            {"id": 3, "cantidad": 3, "precio": "5.00"},
        ]

    @task
    def transformar(filas):
        from decimal import Decimal
        return [
            {**f, "total": str(
                Decimal(f["precio"]) * f["cantidad"]
            )}
            for f in filas
        ]

    @task(retries=0)
    def validar(filas):
        from decimal import Decimal
        if not filas:
            raise ValueError("Lote vacio")
        ids = [f["id"] for f in filas]
        if len(ids) != len(set(ids)):
            raise ValueError("Identificadores duplicados")
        for f in filas:
            if f["cantidad"] <= 0 or Decimal(f["precio"]) < 0:
                raise ValueError(f"Venta invalida: {f['id']}")
        return filas

    @task
    def cargar(filas):
        import hashlib
        import json
        import logging
        from pathlib import Path
        context = get_current_context()
        clave = hashlib.sha256(
            context["run_id"].encode("utf-8")
        ).hexdigest()[:20]
        carpeta = Path("/opt/airflow/logs/s8_resultados")
        carpeta.mkdir(parents=True, exist_ok=True)
        destino = carpeta / f"ventas_{clave}.json"
        temporal = destino.with_suffix(".tmp")
        temporal.write_text(
            json.dumps(filas, indent=2), encoding="utf-8"
        )
        temporal.replace(destino)
        logging.info("Filas=%s; salida=%s", len(filas), destino)
        return {"filas": len(filas), "ruta": str(destino)}

    cargar(validar(transformar(extraer())))

ventas()
