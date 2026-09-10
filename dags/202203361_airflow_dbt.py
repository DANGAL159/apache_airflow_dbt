"""Pipeline de ventas del estudiante 202203361. Editar y entregar mediante PR."""
from datetime import timedelta
import logging
import pendulum
from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLCheckOperator

CARNET = "202203361"
ESQUEMA = f"alumno_{CARNET}"
PROYECTO = "/opt/airflow/workshop/current/dbt/sgfood"
OPCIONES = (
    f" --project-dir {PROYECTO} --profiles-dir /opt/airflow/dbt_config"
    f" --target dev --target-path /opt/airflow/logs/dbt/{CARNET}/target"
    f" --log-path /opt/airflow/logs/dbt/{CARNET}/logs"
)

@dag(
    dag_id=f"estudiante_{CARNET}_dbt",
    schedule=None,
    start_date=pendulum.datetime(2026, 9, 1, tz="America/Guatemala"),
    catchup=False,
    max_active_runs=1,
    default_args={"execution_timeout": timedelta(minutes=10)},
    tags=["semana8", "estudiante", CARNET],
    description=f"Pipeline dbt de {CARNET}; revisar el grafo y sus logs.",
)
def pipeline_estudiante():
    @task
    def presentar():
        logging.info("Carnet=%s; esquema=%s", CARNET, ESQUEMA)
        return {"carnet": CARNET, "esquema": ESQUEMA}

    cargar = BashOperator(
        task_id="cargar_raw",
        bash_command="/opt/airflow/dbt_venv/bin/dbt seed" + OPCIONES,
        env={"DBT_SCHEMA": ESQUEMA}, append_env=True, pool="dbt_pool",
    )
    transformar = BashOperator(
        task_id="transformar_y_probar",
        bash_command="/opt/airflow/dbt_venv/bin/dbt build" + OPCIONES,
        env={"DBT_SCHEMA": ESQUEMA}, append_env=True, pool="dbt_pool",
    )
    verificar = SQLCheckOperator(
        task_id="verificar_ventas",
        conn_id="warehouse_sgfood",
        sql=f"SELECT COUNT(*) = 10, COUNT(DISTINCT venta_id) = 10 FROM {ESQUEMA}_marts.fact_ventas",
    )
    # Personaliza la validacion: agrega un control del total neto esperado.
    presentar() >> cargar >> transformar >> verificar

pipeline_estudiante()
