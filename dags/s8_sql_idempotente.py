"""Ejecuta dos veces el UPSERT del documento y comprueba una sola venta."""
import pendulum
from airflow.sdk import dag
from airflow.providers.common.sql.operators.sql import SQLCheckOperator, SQLExecuteQueryOperator

SQL_CARGA = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE TABLE IF NOT EXISTS raw.ventas (
    venta_id INTEGER PRIMARY KEY,
    fecha DATE NOT NULL,
    total NUMERIC(12,2) NOT NULL CHECK (total >= 0)
);
INSERT INTO raw.ventas (venta_id, fecha, total)
VALUES (1, DATE '2026-03-09', 50.00)
ON CONFLICT (venta_id) DO UPDATE
SET fecha = EXCLUDED.fecha, total = EXCLUDED.total;
"""


@dag(
    dag_id="s8_sql_idempotente",
    schedule=None,
    start_date=pendulum.datetime(2026, 9, 1, tz="America/Guatemala"),
    catchup=False,
    max_active_runs=1,
    tags=["semana8", "sql", "idempotencia"],
)
def sql_idempotente():
    primera = SQLExecuteQueryOperator(
        task_id="primera_carga", conn_id="warehouse_sgfood", sql=SQL_CARGA,
    )
    repetir = SQLExecuteQueryOperator(
        task_id="repetir_carga", conn_id="warehouse_sgfood", sql=SQL_CARGA,
    )
    verificar = SQLCheckOperator(
        task_id="verificar_una_venta",
        conn_id="warehouse_sgfood",
        sql="SELECT COUNT(*) = 1, SUM(total) = 50.00 FROM raw.ventas WHERE venta_id = 1",
    )
    primera >> repetir >> verificar


sql_idempotente()
