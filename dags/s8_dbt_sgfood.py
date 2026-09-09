"""Orquesta el proyecto PostgreSQL de la semana 7 en un warehouse local."""
from datetime import timedelta
import csv
from pathlib import Path

import pendulum
from airflow.sdk import dag, task
from airflow.providers.common.sql.operators.sql import SQLCheckOperator
from airflow.providers.standard.operators.bash import BashOperator

PROYECTO = "/opt/airflow/workshop/current/dbt/sgfood"
DBT = "/opt/airflow/dbt_venv/bin/dbt"
OPCIONES = (
    f" --project-dir {PROYECTO} --profiles-dir /opt/airflow/dbt_config --target dev"
    " --target-path /opt/airflow/logs/dbt/docente/target"
    " --log-path /opt/airflow/logs/dbt/docente/logs"
)


@dag(
    dag_id="s8_dbt_sgfood",
    schedule=None,
    start_date=pendulum.datetime(2026, 9, 1, tz="America/Guatemala"),
    catchup=False,
    max_active_runs=1,
    default_args={"execution_timeout": timedelta(minutes=10)},
    tags=["semana8", "dbt", "sgfood"],
    description="CSV de semana 7 -> raw con dbt seed -> dbt build -> conciliacion SQL.",
)
def dbt_sgfood():
    @task
    def revisar_fuentes():
        resumen = {}
        for nombre in ("clientes", "productos", "sucursales", "ventas"):
            ruta = Path(PROYECTO) / "seeds" / "raw" / f"{nombre}.csv"
            if any(not linea.strip() for linea in ruta.read_text(encoding="utf-8-sig").splitlines()):
                raise ValueError(f"Fuente con lineas vacias: {nombre}; normalizar el CSV antes de dbt seed")
            with ruta.open(encoding="utf-8-sig", newline="") as archivo:
                filas = list(csv.DictReader(archivo))
            if not filas:
                raise ValueError(f"Fuente vacia: {nombre}")
            resumen[nombre] = len(filas)
        return resumen

    cargar_raw = BashOperator(
        task_id="cargar_raw", bash_command=DBT + " seed" + OPCIONES, pool="dbt_pool",
    )
    construir = BashOperator(
        task_id="construir_modelos_dbt", bash_command=DBT + " build" + OPCIONES, pool="dbt_pool",
    )
    verificar = SQLCheckOperator(
        task_id="verificar_mart",
        conn_id="warehouse_sgfood",
        sql="""
        SELECT
            COUNT(*) > 0,
            COUNT(*) = COUNT(DISTINCT venta_id),
            COUNT(*) = (SELECT COUNT(*) FROM analytics_raw.ventas),
            SUM(monto_neto) = (
                SELECT SUM(cantidad * (precio_unitario - descuento_unitario))
                FROM analytics_raw.ventas
            )
        FROM analytics_marts.fact_ventas
        """,
    )
    revisar_fuentes() >> cargar_raw >> construir >> verificar


dbt_sgfood()
