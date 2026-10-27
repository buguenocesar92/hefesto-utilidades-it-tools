# ayudante: kit de pruebas aislado para hefesto-utilidades-it-tools.
#
# Nunca toca el .env real: el kit se copia a un directorio temporal con un
# .env sintetico. Este kit es SIN ESTADO: no hay Docker, ni volumenes, ni base
# de datos. El unico material sensible es el .env (hash bcrypt de Basic Auth).
RAIZ="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
export RAIZ
export HEFESTO_KIT_TEST=1

preparar_kit() {
  KIT="$BATS_TEST_TMPDIR/kit"
  rm -rf "$KIT"
  mkdir -p "$KIT"
  cp -R "$RAIZ/scripts" "$KIT/scripts"
  rm -rf "$KIT/scripts/__pycache__"
  for extra in compose.yaml compose.bootstrap.yaml .env.example; do
    if [ -f "$RAIZ/$extra" ]; then cp "$RAIZ/$extra" "$KIT/$extra"; fi
  done
  if [ -d "$RAIZ/ops" ]; then cp -R "$RAIZ/ops" "$KIT/ops"; fi
  mkdir -p "$KIT/backups"
  printf 'BASIC_AUTH_USER=prueba\nBASIC_AUTH_HASH=valor-ficticio-no-real\n' > "$KIT/.env"
  chmod 600 "$KIT/.env"
  export KIT
}

respaldo_reciente() {
  ls -d "$KIT"/backups/*/ 2>/dev/null | head -1
}

generar_receptor_age() {
  # Genera un par de claves age efimero SOLO en el directorio temporal de la
  # prueba. Nunca se versiona ni se usa fuera de la suite.
  if ! command -v age-keygen >/dev/null 2>&1; then
    return 1
  fi
  local dir="$BATS_TEST_TMPDIR/age"
  mkdir -p "$dir"
  chmod 700 "$dir"
  # age-keygen escribe la clave publica en stderr y la deja en el encabezado
  # del archivo de clave privada.
  if ! age-keygen -o "$dir/clave.txt" >/dev/null 2>&1; then
    return 1
  fi
  AGE_RECIPIENT="$(sed -n 's/^# public key: //p' "$dir/clave.txt")"
  export AGE_RECIPIENT
  [ -n "$AGE_RECIPIENT" ]
}
