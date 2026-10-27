#!/usr/bin/env python3
"""Respaldo de hefesto-utilidades-it-tools (IT Tools tras Caddy con Basic Auth).

Reglas de material sensible:
- El .env NUNCA se copia en claro: solo env.vars (nombres de las variables) y,
  si hay receptor age, el .env cifrado (env.age).
- Sin receptor age el respaldo sale SIN el .env y el manifiesto lo declara.
  No existe modo degradado a texto plano.
- manifest.json lleva siempre software, version, database, sha256 y status.

Ver docs/CONTRATO-RESPALDO.md.
"""
import datetime
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo_contrato import (ejecutar, escribir_manifiesto, exportar_env,
                               marcar_fallido, receptor_age)

SOFTWARE = "hefesto-utilidades-it-tools"
VERSION = "2026.9.27"
# El kit es SIN ESTADO: no hay base de datos que respaldar.
DATABASE = "none"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)

# Material de configuracion que si puede viajar en claro.
ARCHIVOS = ["compose.yaml", "compose.bootstrap.yaml", "ops/Caddyfile", "ops/start.sh"]
VARS_RECIPIENTE = ("AGE_RECIPIENT", "SOPS_AGE_RECIPIENT")


def receptor_del_env() -> str:
    """Clave publica age declarada en el .env del kit.

    Solo se usa si el operador no la exporto en el entorno. No se imprime ni
    se escribe en ningun sitio: el respaldo usa unicamente la parte publica.
    """
    origen = RAIZ / ".env"
    if not origen.is_file():
        return ""
    for linea in origen.read_text(encoding="utf-8", errors="replace").splitlines():
        texto = linea.strip()
        if not texto or texto.startswith("#") or "=" not in texto:
            continue
        clave, valor = texto.split("=", 1)
        clave = clave.strip()
        valor = valor.strip().strip("'\"")
        if clave in VARS_RECIPIENTE and valor:
            return valor
    return ""


def main():
    if not (RAIZ / ".env").is_file():
        raise SystemExit("Falta .env: el kit no se puede respaldar sin el archivo real.")
    for nombre in ARCHIVOS:
        if not (RAIZ / nombre).is_file():
            raise SystemExit("Falta archivo: " + nombre)

    if not receptor_age():
        candidato = receptor_del_env()
        if candidato:
            os.environ["AGE_RECIPIENT"] = candidato

    carpeta = RAIZ / "backups" / datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ")
    carpeta.mkdir(parents=True, mode=0o700)
    try:
        for nombre in ARCHIVOS:
            destino = carpeta / nombre
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ / nombre, destino)
        meta = exportar_env(RAIZ, carpeta)
        artefactos = [n for n in ARCHIVOS if (carpeta / n).is_file()]
        artefactos.append("env.vars")
        if (carpeta / "env.age").is_file():
            artefactos.append("env.age")
        escribir_manifiesto(carpeta, SOFTWARE, VERSION, DATABASE, artefactos, extra=meta)
    except Exception:
        marcar_fallido(carpeta, SOFTWARE, VERSION, DATABASE)
        raise
    print("Respaldo completo:", carpeta)
    print("El .env no viaja en claro: solo nombres de variables, o cifrado con age.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
