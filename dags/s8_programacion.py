"""Calendario diario con intervalo explicito; queda pausado para exploracion."""
import logging

import pendulum
from airflow.sdk import dag, get_current_context, task
from airflow.timetables.interval import CronDataIntervalTimetable


@dag(
    dag_id="s8_programacion",
    schedule=CronDataIntervalTimetable("0 0 * * *", timezone="America/Guatemala"),
    start_date=pendulum.datetime(2026, 9, 1, tz="America/Guatemala"),
    catchup=False,
    max_active_runs=1,
    tags=["semana8", "programacion"],
)
def programacion():
    @task
    def mostrar_intervalo():
        context = get_current_context()
        resultado = {
            "run_id": context["run_id"],
            "inicio": str(context["data_interval_start"]),
            "fin_exclusivo": str(context["data_interval_end"]),
        }
        logging.info("Periodo del lote: %s", resultado)
        return resultado

    mostrar_intervalo()


programacion()
