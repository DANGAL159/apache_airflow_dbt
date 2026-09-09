"""Inicializa volumenes de demostracion sin sobrescribir credenciales existentes."""
import json
import os
from pathlib import Path

for name in ("logs", "auth"):
    path = Path("/opt/airflow") / name
    path.mkdir(parents=True, exist_ok=True)
    os.chown(path, 50000, 0)
    os.chmod(path, 0o775)
passwords = Path("/opt/airflow/auth/passwords.json")
if not passwords.exists():
    passwords.write_text(json.dumps({"admin": "admin", "estudiantes": "estudiantes"}))
os.chown(passwords, 50000, 0)
os.chmod(passwords, 0o640)
print("Volumenes locales preparados")
