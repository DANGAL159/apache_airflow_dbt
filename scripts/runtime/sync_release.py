"""Activa un paquete validado usando una referencia atomica dentro del volumen."""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path("/opt/ss2-airflow-dbt")

def token():
    request = urllib.request.Request(
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
        headers={"Metadata-Flavor": "Google"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)["access_token"]

def object_bytes(bucket, name, access_token):
    url = f"https://storage.googleapis.com/storage/v1/b/{bucket}/o/{urllib.parse.quote(name, safe='')}?alt=media"
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + access_token})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()

def main():
    config = json.loads((ROOT / "runtime/platform.json").read_text())
    access_token = token()
    try:
        manifest = json.loads(object_bytes(config["bucket"], "current.json", access_token))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            print("Aun no hay despliegue desde GitHub; se conserva bootstrap")
            return
        raise
    revision = manifest["revision"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Revision invalida")
    live = ROOT / "live"
    release = live / "releases" / revision
    if (live / "current").resolve() == release:
        print("Sin cambios:", revision)
        return
    payload = object_bytes(config["bucket"], manifest["object"], access_token)
    if hashlib.sha256(payload).hexdigest() != manifest["sha256"]:
        raise ValueError("El SHA-256 del paquete no coincide")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for entry in archive.infolist():
            path = Path(entry.filename)
            if path.is_absolute() or ".." in path.parts or path.parts[0] not in {"dags", "dbt"}:
                raise ValueError("Ruta no permitida en el paquete")
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("El paquete no admite enlaces simbolicos")
        archive.extractall(release)
    # Permisos de lectura para el UID 50000 del contenedor.
    for directory, _, files in os.walk(release):
        os.chmod(directory, 0o755)
        for name in files:
            os.chmod(Path(directory) / name, 0o644)
    temporary = live / "current.next"
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(Path("releases") / revision, target_is_directory=True)
    temporary.replace(live / "current")
    (ROOT / "runtime/deployed.json").write_text(json.dumps(manifest, indent=2))
    print("Revision activada:", revision)

if __name__ == "__main__":
    main()
