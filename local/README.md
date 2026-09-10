# Base local para estudiantes

Desde una copia **completa del repositorio**, entrar a esta carpeta y ejecutar:

```bash
cd local
docker compose up
```

También puedes usar `docker compose up -d` para dejarlo en segundo plano. El primer arranque construye la imagen, prepara permisos, crea las bases y configura Airflow automáticamente. No debes crear `.env`, instalar Python en tu equipo ni ejecutar migraciones manuales.

Requisitos: Docker Desktop iniciado con contenedores Linux y Compose v2; reservar al menos 4 GB de RAM para Docker, preferiblemente 8 GB. La descarga inicial requiere conexión a Internet y puede tardar varios minutos.

## Acceso

- **http://localhost:8084**
- Usuario administrador local: **admin**, contraseña: **admin**.
- Usuario de consulta: **estudiantes**, contraseña: **estudiantes**.

Estas credenciales son de demostración local. Los servicios se publican únicamente en el equipo local. GCP tiene sus propias cuentas y contraseña.

`prepare` y `airflow-init` deben terminar con código 0. Los servicios permanentes son API server, scheduler, DAG processor y dos PostgreSQL. El entorno usa LocalExecutor para reducir recursos; ejecuta los mismos DAGs que GCP.

## Crear tu DAG

Los directorios `../dags`, `../dbt` y `../dbt_config` se montan desde la raíz del repositorio. Esta carpeta no se debe copiar aislada del resto del proyecto.

En Codespaces puedes usar el generador del README principal. Para generarlo con Docker desde `local/`, sin instalar Python:

En PowerShell:

```powershell
$repoPath = (Resolve-Path ..).Path
docker compose run --rm --no-deps --entrypoint python -v "${repoPath}:/workspace" -w /workspace airflow-scheduler scripts/crear_dag.py TU_CARNET
docker compose run --rm --no-deps --entrypoint python -v "${repoPath}:/workspace" -w /workspace airflow-scheduler scripts/validar_dags.py
```

En Linux o macOS (Bash):

```bash
docker compose run --rm --no-deps --user "$(id -u):0" --entrypoint python -v "$(cd .. && pwd):/workspace" -w /workspace airflow-scheduler scripts/crear_dag.py TU_CARNET
docker compose run --rm --no-deps --user "$(id -u):0" --entrypoint python -v "$(cd .. && pwd):/workspace" -w /workspace airflow-scheduler scripts/validar_dags.py
```

Sustituye `TU_CARNET` por tu carnet numérico completo. Edita `../dags/TU_CARNET_airflow_dbt.py`; agrega la validación del total neto **3766.75** a `verificar_ventas`. Airflow detecta el archivo, aunque puede tardar unos minutos en mostrarlo.

## Probar

1. Abrir `estudiante_<carnet>_dbt` y habilitarlo si está pausado.
2. Pulsar **Trigger** y esperar que las cuatro tareas terminen en `success`.
3. Revisar los logs de `transformar_y_probar`: dbt debe aprobar sus 38 pruebas.
4. Ejecutar otra vez y comprobar que permanecen 10 ventas únicas.

```bash
docker compose exec warehouse psql -U sgfood -d sgfood_dw -c "SELECT COUNT(*) AS ventas, COUNT(DISTINCT venta_id) AS ventas_unicas, SUM(monto_neto) AS total_neto FROM alumno_TU_CARNET_marts.fact_ventas;"
```

Resultado esperado: **10 / 10 / 3766.75**. El carnet ficticio `202600001` ya está incluido para probar inmediatamente.

La verificación del 9 de septiembre de 2026 comprobó el arranque automático, ocho ejecuciones exitosas y una falla de calidad intencional, incluido un reintento automático y una recuperación. Las 38 pruebas dbt aprobaron en ambos esquemas y la segunda ejecución estudiantil conservó el resultado esperado. Los resultados están en [verificacion_local.json](../evidencias/verificacion_local.json).

Para repetir la comprobación automática en un entorno nuevo, cuando Airflow ya muestre los DAGs:

```bash
docker compose exec airflow-scheduler python /opt/airflow/local/verify.py start
docker compose exec airflow-scheduler python /opt/airflow/local/verify.py status
```

Consultar `status` nuevamente hasta obtener `Verificacion completa: True`. `start` registra una sola batería por volumen de logs; `status` permite revisar sus ejecuciones posteriormente.

Para explorar los fallos, ejecutar `s8_fallos_controlados` con `fallo_transitorio=true` o `dato_invalido=true`. En el segundo caso, `validar` falla y `publicar` queda bloqueada. Una ejecución nueva con ambos parámetros en `false` termina correctamente.

## Diagnóstico y cierre

```bash
docker compose ps -a
docker compose exec airflow-scheduler airflow dags list-import-errors
docker compose logs --tail 80 airflow-api-server
docker compose logs --tail 80 airflow-dag-processor
docker compose down
```

Los datos, logs y credenciales persisten en volúmenes de Docker. `down` los conserva. Si el puerto 8084 está ocupado, libera ese puerto antes del arranque. Los pipelines locales no escriben en GCP.

Después de comprobar tu DAG, sube únicamente tu archivo y las evidencias solicitadas a tu rama y abre el PR hacia el repositorio del curso.
