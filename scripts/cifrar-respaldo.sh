#!/usr/bin/env bash
# =============================================================================
# Cifra un respaldo de hefesto-utilidades-it-tools con age.
#
# - NO borra el original: escribe <respaldo>.tar.gz.age al lado.
# - NO existe modo degradado a texto plano: sin receptor age no hace nada.
# - La clave publica del receptor es un INSUMO EXTERNO: la define el
#   operador (AGE_RECIPIENT o AGE_RECIPIENTE). El script no genera claves.
#
# Uso: ./scripts/cifrar-respaldo.sh RUTA_RESALDO
# =============================================================================
set -euo pipefail

ORIGEN="${1:?uso: cifrar-respaldo.sh RUTA_RESALDO}"
PUBKEY="${AGE_RECIPIENT:-${AGE_RECIPIENTE:-}}"

if [ -z "${PUBKEY}" ]; then
  echo "falta AGE_RECIPIENT: la clave publica age del receptor" >&2
  echo "Es un insumo externo: no se genera aqui. Definala en el entorno." >&2
  exit 1
fi

command -v age >/dev/null || { echo "age no esta instalado" >&2; exit 1; }
[ -e "${ORIGEN}" ] || { echo "no existe: ${ORIGEN}" >&2; exit 1; }

tar czf - -C "$(dirname "${ORIGEN}")" "$(basename "${ORIGEN}")" \
  | age -r "${PUBKEY}" -o "${ORIGEN}.tar.gz.age"

sha256sum "${ORIGEN}.tar.gz.age" > "${ORIGEN}.tar.gz.age.sha256"
echo "Cifrado: ${ORIGEN}.tar.gz.age (el original NO se borra)"
