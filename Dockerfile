FROM apache/airflow:3.1.1-python3.12

# dbt lives in a separate environment to avoid changing Airflow dependencies.
RUN python -m venv /opt/airflow/dbt_venv \
    && /opt/airflow/dbt_venv/bin/pip install --no-cache-dir \
       dbt-core==1.8.9 dbt-postgres==1.8.2 \
    && python -c "from airflow.providers.postgres.hooks.postgres import PostgresHook; from airflow.providers.common.sql.operators.sql import SQLCheckOperator; from airflow.providers.standard.operators.bash import BashOperator"

ENV DBT_EXECUTABLE="/opt/airflow/dbt_venv/bin/dbt"
