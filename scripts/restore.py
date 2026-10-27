#!/usr/bin/env python3
"""Restauracion de la configuracion de hefesto-utilidades-it-tools.

Sin --confirmar CONFIRMAR_RESTAURACION no se escribe nada; con --dry-run se
simula. El destino debe estar VACIO: nunca se sobrescribe configuracion
existente. El .env NO viaja en el respaldo: se restaura en claro solo si el
respaldo lo traia cifrado y el operador entrega su clave privada
(AGE_IDENTITY_FILE), que es un insumo externo.

Ver docs/CONTRATO-RESPALDO.md.
"""
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo_contrato import (CONFIRMACION, RespaldoError, auditar, descifrar_con_age,
                               ejecutar, ejecutar_check, escribir_informe)

SOFTWARE = "hefesto-utilidades-it-tools"
VERSION = "2026.9.27"
DATABASE = "none"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)
ARCHIVOS = ["compose.yaml", "compose.bootstrap.yaml", "ops/Caddyfile", "ops/start.sh"]


def parsear(argv):
    """Interpreta origen, destino, --dry-run y --confirmar CONFIRMAR_RESTAURACION."""
    modo = None
    origen = None
    destino = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--dry-run":
            if modo == "confirmado":
                raise RespaldoError("No se pueden combinar --dry-run y --confirmar", 1)
            modo = "dry-run"
        elif arg == "--confirmar":
            if i + 1 >= len(argv):
                raise RespaldoError("Falta el valor de --confirmar", 1)
            if argv[i + 1] != CONFIRMACION:
                raise RespaldoError("El valor de --confirmar debe ser " + CONFIRMACION, 1)
            if modo == "dry-run":
                raise RespaldoError("No se pueden combinar --dry-run y --confirmar", 1)
            modo = "confirmado"
            i += 1
        elif arg.startswith("-"):
            raise RespaldoError("Opcion desconocida: " + arg, 1)
        else:
            if origen is None:
                origen = arg
            elif destino is None:
                destino = arg
            else:
                raise RespaldoError("Solo se admiten ORIGEN y DESTINO", 1)
        i += 1
    if origen is None or destino is None:
        raise RespaldoError("Uso: python3 scripts/restore.py /ruta/respaldo /ruta/destino "
                            "[--dry-run|--confirmar " + CONFIRMACION + "]", 1)
    if modo is None:
        raise RespaldoError("Falta --confirmar " + CONFIRMACION +
                            " (o --dry-run para simular sin escribir)", 3)
    return modo, origen, destino


def main():
    modo, origen, destino = parsear(sys.argv[1:])
    origen = Path(origen).resolve()
    destino = Path(destino).resolve()
    ejecutar_check(str(origen), SOFTWARE, VERSION, DATABASE)
    if modo == "dry-run":
        print("Simulacion: el respaldo es integro y no se escribio nada.")
        print("Para restaurar de verdad: --confirmar " + CONFIRMACION)
        return 0
    if destino.exists() and any(destino.iterdir()):
        raise RespaldoError("El destino no esta vacio; no se sobrescribe nada. "
                            "Use un destino nuevo.", 5)
    destino.mkdir(parents=True, exist_ok=True, mode=0o700)
    for nombre in ARCHIVOS:
        origen_archivo = origen / nombre
        if not origen_archivo.is_file():
            raise RespaldoError("Falta el artefacto en el respaldo: " + nombre, 2)
        copia = destino / nombre
        copia.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen_archivo, copia)
    if (origen / "env.vars").is_file():
        shutil.copy2(origen / "env.vars", destino / "env.vars")
    if (origen / "env.age").is_file():
        # El .env viaja cifrado. Restaurarlo en claro exige la clave privada
        # del receptor: es un insumo externo y no se genera aqui.
        try:
            descifrar_con_age(origen / "env.age", destino / ".env")
            os.chmod(destino / ".env", 0o600)
            print("El .env se restauro descifrado: revisa que el hash bcrypt sea el del destino.")
        except RespaldoError as exc:
            print("El .env NO se restauro: " + str(exc))
            print("Se conserva cifrado (env.age) en el destino para restaurarlo con la clave.")
            shutil.copy2(origen / "env.age", destino / "env.age")
    else:
        print("El respaldo no trae el .env cifrado: genera uno nuevo en el destino con "
              "scripts/configure.py y cambia BASIC_AUTH_HASH.")
    escribir_informe(origen, software=SOFTWARE, version=VERSION, database=DATABASE,
                     modo="confirmado", resultado="restaurado", destino=str(destino))
    auditar(RAIZ, operacion="restore", kit=SOFTWARE, origen=str(origen),
            destino=str(destino), resultado="restaurado")
    print("Configuracion restaurada en", destino)
    print("Revisar y arrancar primero por tunel privado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
