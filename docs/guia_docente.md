# Guía docente

## Dinámica

La modalidad por fork permite que cada estudiante abra Codespaces y entregue su DAG sin dar permisos de escritura general sobre el repositorio. No se necesita portal de invitaciones para esta modalidad. Quienes ya tengan acceso de escritura pueden usar una rama propia.

1. Mostrar `s8_ventas`, su grafo y el archivo producido.
2. Ejecutar `s8_dbt_sgfood`: 10 ventas, total neto 3766.75, pruebas de calidad.
3. Mostrar el generador con un carnet de ejemplo y los esquemas `alumno_<carnet>_raw`, `_staging`, `_intermediate` y `_marts`.
4. Pedir que agreguen un control de `SUM(monto_neto) = 3766.75` en su tarea SQL.
5. Revisar los PR: identificadores, consultas, dependencias y ausencia de efectos secundarios al importar. `validate` comprueba estructura e importación, no demuestra que la lógica sea correcta.
6. Fusionar y esperar el workflow de despliegue. La sincronización ocurre cada minuto; el descubrimiento de DAGs puede añadir algunos minutos.
7. Habilitar el DAG del estudiante y ejecutar manualmente. Consultar su última tarea y las evidencias.

La rama principal requiere el check `validate` y revisión del propietario del código. No deben fusionarse cambios no revisados a workflows, Dockerfile, scripts ni Terraform.

## Acceso

- `admin`: docente; puede ejecutar y administrar DAGs.
- `estudiantes`: consulta de DAGs, ejecuciones y logs.

Las contraseñas se obtienen con `terraform output -raw admin_password` y `terraform output -raw viewer_password` en `infra/terraform`. Compartir solamente la contraseña de estudiantes con el grupo.

## Fallos controlados

En `s8_fallos_controlados`, `fallo_transitorio=true` provoca un fallo inicial y éxito en el segundo intento. `dato_invalido=true` hace fallar validar y bloquea publicar. Una ejecución nueva con ambos parámetros en falso debe terminar correctamente.

## Consultas de operación

Desde la VM, usar siempre:

```bash
cd /opt/ss2-airflow-dbt
sudo docker compose --env-file runtime/.env -f runtime/docker-compose.yml ps
sudo docker compose --env-file runtime/.env -f runtime/docker-compose.yml exec -T airflow-scheduler airflow dags list-import-errors
sudo journalctl -u ss2-airflow-dbt-sync.service --no-pager -n 30
sudo cat runtime/deployed.json
```

El laboratorio utiliza un único host y datos de ejemplo. La cuenta de runtime solo puede leer el bucket del taller y su secreto; la cuenta de GitHub puede publicar objetos en ese bucket, sin administrar la VM.
