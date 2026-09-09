# Infraestructura del taller

Cuenta de operación: `javier.valdez.dev@gmail.com`. Proyecto: `project-643d2a1a-b690-4d08-b00`. Los nombres comienzan con `ss2-airflow-dbt`; no reutilizan el estado Terraform de la semana 4.

Recursos: VM e2-standard-4 (4 vCPU, 16 GB), disco pd-balanced de 50 GB, IP estática, VPC, reglas HTTPS y SSH por IAP, bucket privado versionado, secreto, cuentas de servicio y Workload Identity Federation restringida al workflow de este repositorio en `main`.

## Aplicar

En PowerShell, desde esta carpeta:

```powershell
terraform init
terraform validate
$env:GOOGLE_OAUTH_ACCESS_TOKEN = gcloud auth print-access-token --account=javier.valdez.dev@gmail.com
terraform plan '-out=taller.tfplan'
terraform apply taller.tfplan
Remove-Item Env:GOOGLE_OAUTH_ACCESS_TOKEN
terraform output airflow_url
```

Revisar el plan antes de aplicarlo. El estado se conserva localmente, contiene valores sensibles y está excluido por Git. Guardar una copia protegida si se cambia de equipo. No ejecutar `apply` desde otro checkout sin ese estado.

Variables de GitHub Actions a configurar desde los outputs:

| Variable GitHub | Output Terraform |
| --- | --- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `workload_identity_provider` |
| `GCP_DEPLOY_SERVICE_ACCOUNT` | `github_service_account` |
| `GCP_DAG_BUCKET` | `dag_bucket` |

## Entrar por SSH

```powershell
gcloud compute ssh ss2-airflow-dbt --zone=us-central1-a --project=project-643d2a1a-b690-4d08-b00 --account=javier.valdez.dev@gmail.com --tunnel-through-iap
```

El primer arranque instala Docker y construye Airflow/dbt. Consultar `/var/log/syslog` o `journalctl -u google-startup-scripts.service` si tarda. HTTPS usa Caddy con un nombre de sslip.io asociado a la IP; se puede indicar un dominio propio con la variable `domain`.

## Pausar cómputo al terminar la clase

```powershell
gcloud compute instances stop ss2-airflow-dbt --zone=us-central1-a --project=project-643d2a1a-b690-4d08-b00 --account=javier.valdez.dev@gmail.com
gcloud compute instances start ss2-airflow-dbt --zone=us-central1-a --project=project-643d2a1a-b690-4d08-b00 --account=javier.valdez.dev@gmail.com
```

Al detener la VM se conservan disco, IP, bucket y secretos, que pueden mantener cargos. Para retirar definitivamente el taller, revisar `terraform plan -destroy`; destruir la VM elimina su disco y los datos del laboratorio. El bucket no se vacía automáticamente (`force_destroy=false`).

Los cambios en DAGs/dbt viajan por GitHub Actions. Los cambios de infraestructura o de imagen requieren revisar y aplicar Terraform y comprobar el arranque; no se despliegan automáticamente desde un PR estudiantil.
