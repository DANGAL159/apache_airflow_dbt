"""Empaqueta solamente DAGs y fuentes dbt; excluye secretos y resultados locales."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("revision")
    parser.add_argument("--output", default=".generated")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        parser.error("Se requiere un SHA completo de Git")
    root = Path(__file__).resolve().parents[1]
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{args.revision}.zip"
    paths = list((root / "dags").glob("*.py"))
    for path in (root / "dbt").rglob("*"):
        if path.is_file() and not set(path.parts) & {"target", "logs", "dbt_packages", "__pycache__"} and path.suffix in {".sql", ".yml", ".csv"} and not path.name.startswith("."):
            paths.append(path)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for path in sorted(paths):
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, path.read_bytes())
    manifest = {"revision": args.revision, "object": f"releases/{args.revision}.zip", "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}
    (output / "current.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest))

if __name__ == "__main__":
    main()
