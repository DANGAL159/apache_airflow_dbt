# Taller colaborativo: Apache Airflow y dbt

Semana 8 — Seminario de Sistemas 2, USAC. Cada estudiante crea un DAG en GitHub Codespaces y lo entrega por pull request. Después de la revisión del docente, GitHub Actions publica los DAGs y modelos en GCP; Airflow los incorpora automáticamente.

**Versiones:** Airflow 3.1.1, Python 3.12, dbt Core 1.8.9 y dbt-postgres 1.8.2. La infraestructura se administra con Terraform.

## Para estudiantes

1. Crear un **fork** de este repositorio en tu cuenta de GitHub. Si ya tienes permiso de escritura, también puedes trabajar en una rama del repositorio del curso.
2. En tu fork: **Code → Codespaces → Create codespace on main**. Esperar a que termine la preparación del entorno.
3. En la terminal:

```bash
source .venv/bin/activate
git switch -c entrega/TU_CARNET
python scripts/crear_dag.py TU_CARNET
```

Reemplaza `TU_CARNET` por tu carnet numérico completo. Edita el archivo generado en `dags/`, agrega una validación SQL del total neto y explica tu decisión en el PR.

El único archivo que debes modificar y entregar es `dags/TU_CARNET_airflow_dbt.py`. En la tarea `verificar_ventas`, agrega `SUM(monto_neto) = 3766.75` a la consulta SQL, conservando las comprobaciones de conteo y unicidad. Mantén tu carnet, esquema y dependencias. No necesitas modificar los ejemplos, `dbt/`, `dbt_config/`, `local/`, el `Dockerfile` ni los workflows. La infraestructura cloud es administrada por el docente fuera de los archivos publicados del taller.

```bash
python scripts/validar_dags.py
git add dags/TU_CARNET_airflow_dbt.py
git commit -m "Agregar pipeline de ventas de TU_CARNET"
git push -u origin entrega/TU_CARNET
```

4. Abrir un pull request hacia **SS2-USAC/apache_airflow_dbt → main**.
5. El check `validate` debe terminar en verde. Corrige tu rama si falla.
6. El docente revisa y fusiona. Tras la publicación y sincronización, tu DAG aparece como `estudiante_<carnet>_dbt`.
7. El docente ejecuta el DAG. Con la cuenta `estudiantes` puedes consultar el grafo, ejecuciones y logs.

No se necesitan credenciales de GCP en Codespaces. La validación local importa los DAGs, pero no ejecuta dbt ni se conecta al warehouse del curso.

## Ejemplos incluidos

| DAG | Contenido |
| --- | --- |
| `s8_saludo` | TaskFlow y XCom. |
| `s8_ventas` | Extracción, transformación, validación y JSON: 3 ventas, total 95.00. |
| `s8_sql_idempotente` | Dos UPSERT, una venta de 50.00. |
| `s8_dbt_sgfood` | Seeds, modelos y 38 pruebas dbt; 10 ventas, total neto 3766.75. |
| `s8_fallos_controlados` | Parámetros para probar reintentos y errores de calidad. |
| `s8_programacion` | Calendario diario en America/Guatemala. |
| `estudiante_202600001_dbt` | Carnet ficticio reservado para la demostración del flujo estudiantil. |

Cada estudiante usa un esquema base `alumno_<carnet>` y carpetas de resultados propias. Los esquemas evitan colisiones accidentales; los DAGs comparten un entorno de ejecución y deben revisarse antes de fusionarlos. El pool `dbt_pool` limita a dos tareas dbt simultáneas.

## Arquitectura

```text
Fork / rama → Codespaces → Pull request → validate → revisión docente
                                                      ↓ merge main
GitHub Actions → OIDC / WIF → GCS (paquete versionado)
                                      ↓ cada minuto
Compute Engine: Caddy HTTPS → Airflow + Redis + PostgreSQL
                                            ↓
                                  warehouse PostgreSQL
```

El despliegue envía un paquete completo con DAGs y fuentes dbt. La VM verifica su SHA-256 y cambia una referencia de forma atómica. Los paquetes previos se conservan para trazabilidad. Los secretos están en Secret Manager y no se publican en GitHub.

- [Ejecutar y probar en local con Docker Compose](local/README.md)
- [Hoja de trabajo en HTML](docs/hoja_de_trabajo_airflow_dbt.html)
- [Acceso y comprobaciones del despliegue](docs/despliegue.md)
