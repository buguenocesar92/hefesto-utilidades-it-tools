#!/usr/bin/env python3
"""Prepara y valida el .env de hefesto-utilidades-it-tools.

Crea el .env desde .env.example (si no existe) y RECHAZA el valor de ejemplo
del hash bcrypt: si el acceso al gateway queda con una credencial conocida,
el kit esta abierto a cualquiera que lea el repositorio.

Codigos de salida:
  0  .env valido
  2  el .env (o su plantilla) conserva un valor de ejemplo
  3  falta .env.example
"""
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLACEHOLDER = "REEMPLAZAR_HASH_BCRYPT"
MARCADORES = ("REEMPLAZAR", "CAMBIAR", "CHANGE_ME", "GENERAR", "TU_CLAVE", "xxxxx")


def validar(contenido: str) -> None:
    """Falla si el .env conserva un marcador de posicion."""
    if PLACEHOLDER in contenido:
        raise SystemExit(
            "ERROR: BASIC_AUTH_HASH sigue con el valor de ejemplo ("
            + PLACEHOLDER + ").\n"
            "Genera un hash bcrypt real con:\n"
            "  docker run --rm httpd:2.4-alpine htpasswd -nbB hefesto | tr -d '\\n'\n"
            "o con:\n"
            "  python3 -c \"import bcrypt; print(bcrypt.hashpw(b'CLAVE', bcrypt.gensalt()).decode())\"\n"
            "El valor de ejemplo deja el acceso al gateway con una credencial conocida.")
    for marcador in MARCADORES:
        for linea in contenido.splitlines():
            texto = linea.strip()
            if not texto or texto.startswith("#") or "=" not in texto:
                continue
            clave, valor = texto.split("=", 1)
            if clave.strip() != "BASIC_AUTH_HASH":
                continue
            valor = valor.strip().strip("'\"")
            if not valor:
                raise SystemExit("ERROR: BASIC_AUTH_HASH esta vacio.")
            if marcador.lower() in valor.lower():
                raise SystemExit(
                    "ERROR: BASIC_AUTH_HASH contiene un marcador de posicion ("
                    + marcador + "). Genera un hash bcrypt real antes de arrancar.")


def main() -> int:
    destino = RAIZ / ".env"
    plantilla = RAIZ / ".env.example"
    if not plantilla.is_file():
        print("Falta .env.example: no se puede crear el .env.", file=sys.stderr)
        return 3
    if destino.exists():
        print(".env ya existe: no se sobreescribe.")
    else:
        fd = os.open(destino, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(plantilla.read_text(encoding="utf-8"))
        print(".env creado desde .env.example. Configura usuario y hash bcrypt.")
    validar(destino.read_text(encoding="utf-8"))
    print(".env validado: no hay valores de ejemplo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
