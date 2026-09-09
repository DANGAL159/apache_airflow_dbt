"""Pruebas reproducibles de reintentos, validacion y recuperacion."""
from datetime import timedelta
import logging

import pendulum
from airflow.sdk import Param, dag, get_current_context, task


@dag(
    dag_id="s8_fallos_controlados",
    schedule=None,
    start_date=pendulum.datetime(2026, 9, 1, tz="America/Guatemala"),
    catchup=False,
    max_active_runs=1,
    params={
        "fallo_transitorio": Param(False, type="boolean"),
        "dato_invalido": Param(False, type="boolean"),
    },
    tags=["semana8", "fallos", "reintentos"],
    description="Activa parametros al disparar el DAG para observar un retry o un fallo de calidad.",
)
def fallos_controlados():
    @task(retries=1, retry_delay=timedelta(seconds=15))
    def extraer():
        context = get_current_context()
        intento = context["ti"].try_number
        logging.info("Intento de extraccion: %s", intento)
        if context["params"]["fallo_transitorio"] and intento == 1:
            raise ConnectionError("Fallo de red simulado: el segundo intento funcionara")
        return {"id": 1, "cantidad": 2}

    @task(retries=0)
    def validar(venta):
        if get_current_context()["params"]["dato_invalido"]:
            venta = {**venta, "cantidad": -2}
        if venta["cantidad"] <= 0:
            raise ValueError("Fallo controlado: cantidad debe ser positiva")
        return venta

    @task
    def publicar(venta):
        logging.info("Publicacion autorizada: %s", venta)
        return {"publicado": True, "venta_id": venta["id"]}

    publicar(validar(extraer()))


fallos_controlados()
