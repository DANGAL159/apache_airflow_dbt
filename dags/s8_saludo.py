import pendulum
from airflow.sdk import dag, task

@dag(
    dag_id="s8_saludo",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["semana8"],
)
def saludo():
    @task
    def preparar():
        return "SGFood"

    @task
    def mostrar(nombre):
        print(f"Pipeline preparado para {nombre}")

    mostrar(preparar())

saludo()
