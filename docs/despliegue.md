# Acceso al taller en GCP

- Airflow: **https://airflow-dbt.34.59.169.152.sslip.io**
- Repositorio: https://github.com/SS2-USAC/apache_airflow_dbt
- Workflows: https://github.com/SS2-USAC/apache_airflow_dbt/actions
- Cuenta GCP de operación: `javier.valdez.dev@gmail.com`.
- Proyecto: `project-643d2a1a-b690-4d08-b00`.
- VM: `ss2-airflow-dbt`, `us-central1-a`, `e2-standard-4`.
- Bucket: `project-643d2a1a-b690-4d08-b00-s8-airflow-dbt`.

Usuarios: `admin` para el docente y `estudiantes` para consulta. Las contraseñas no se publican en este repositorio. El docente puede obtenerlas desde los outputs sensibles de Terraform.

## Flujo comprobado de publicación

El workflow [34356249342](https://github.com/SS2-USAC/apache_airflow_dbt/actions/runs/34356249342) validó los siete DAGs, se autenticó con Workload Identity Federation y publicó el paquete en GCS. La VM comprobó el hash y activó la revisión `31ac82c1105f785e958223c793eb49fd67d37def`.

La rama `main` exige el check `validate`, una aprobación y revisión de CODEOWNERS. El administrador conserva la capacidad de aplicar correcciones de operación. Los estudiantes trabajan por fork y PR, sin claves de GCP.

La preparación de Python utilizada por Codespaces se ejecutó correctamente en GitHub Actions con Python 3.12. La disponibilidad de la máquina Codespaces de 2 CPU y 8 GB se comprobó por API; no se deja un Codespace personal abierto.
