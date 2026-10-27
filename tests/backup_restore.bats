#!/usr/bin/env bats
# Ciclo backup -> restore de hefesto-utilidades-it-tools con datos sinteticos.
#
# Nunca toca el .env real ni Docker real: el kit se copia a un directorio
# temporal (tests/ayudante.bash) con un .env sintetico.

load 'ayudante.bash'

setup() {
  preparar_kit
  unset AGE_RECIPIENT || true
  unset AGE_RECIPIENTE || true
}

@test "backup.py exige el .env antes de hacer nada" {
  rm -f "$KIT/.env"
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -ne 0 ]
}

@test "backup.py genera el manifiesto con las cinco claves del contrato" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  [ -f "$RESPALDO/manifest.json" ]
  python3 - "$RESPALDO/manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
for clave in ("software", "version", "database", "sha256", "status"):
    assert clave in m, "falta la clave " + clave
assert m["status"] == "completed", m["status"]
assert m["sha256"], "sha256 vacio"
PY
}

@test "el .env no queda en claro dentro del respaldo" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  [ ! -f "$RESPALDO/.env" ]
  [ -f "$RESPALDO/env.vars" ]
  run grep -R -F "valor-ficticio-no-real" "$RESPALDO"
  [ "$status" -ne 0 ]
}

@test "con receptor age el .env viaja cifrado y se descifra byte a byte" {
  if ! generar_receptor_age; then skip "age-keygen no disponible en este entorno"; fi
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  [ -f "$RESPALDO/env.age" ]
  run grep -R -F "valor-ficticio-no-real" "$RESPALDO"
  [ "$status" -ne 0 ]
  age -d -i "$BATS_TEST_TMPDIR/age/clave.txt" "$RESPALDO/env.age" > "$BATS_TEST_TMPDIR/env.plano"
  cmp "$BATS_TEST_TMPDIR/env.plano" "$KIT/.env"
}

@test "check_backup acepta el respaldo integro" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  run python3 "$KIT/scripts/check_backup.py" "$RESPALDO"
  [ "$status" -eq 0 ]
}

@test "check_backup rechaza un artefacto alterado" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  printf 'alterado\n' >> "$RESPALDO/compose.yaml"
  run python3 "$KIT/scripts/check_backup.py" "$RESPALDO"
  [ "$status" -eq 2 ]
}

@test "check_backup rechaza un .env en claro dentro del respaldo" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  cp "$KIT/.env" "$RESPALDO/.env"
  run python3 "$KIT/scripts/check_backup.py" "$RESPALDO"
  [ "$status" -eq 4 ]
}

@test "check_backup rechaza un respaldo no completado" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  python3 -c "import json,sys; p=sys.argv[1]; m=json.load(open(p)); m['status']='failed'; json.dump(m, open(p,'w'))" "$RESPALDO/manifest.json"
  run python3 "$KIT/scripts/check_backup.py" "$RESPALDO"
  [ "$status" -eq 2 ]
}

@test "restore sin --confirmar no restaura" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  run python3 "$KIT/scripts/restore.py" "$RESPALDO" "$BATS_TEST_TMPDIR/destino"
  [ "$status" -eq 3 ]
  [ ! -f "$RESPALDO/restore-report.json" ]
}

@test "restore en dry-run no escribe nada" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  run python3 "$KIT/scripts/restore.py" "$RESPALDO" "$BATS_TEST_TMPDIR/destino" --dry-run
  [ "$status" -eq 0 ]
  [ ! -f "$RESPALDO/restore-report.json" ]
  [ ! -d "$KIT/logs" ]
}

@test "restore con --confirmar restaura en un destino vacio y deja informe y auditoria" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  run python3 "$KIT/scripts/restore.py" "$RESPALDO" "$BATS_TEST_TMPDIR/destino" --confirmar CONFIRMAR_RESTAURACION
  [ "$status" -eq 0 ]
  [ -f "$RESPALDO/restore-report.json" ]
  [ -f "$KIT/logs/restore.log" ]
  [ -f "$BATS_TEST_TMPDIR/destino/compose.yaml" ]
  run grep -F "restore" "$KIT/logs/restore.log"
  [ "$status" -eq 0 ]
}

@test "restore aborta si el destino no esta vacio" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  mkdir -p "$BATS_TEST_TMPDIR/destino"
  printf 'dato previo\n' > "$BATS_TEST_TMPDIR/destino/dato-previo.txt"
  run python3 "$KIT/scripts/restore.py" "$RESPALDO" "$BATS_TEST_TMPDIR/destino" --confirmar CONFIRMAR_RESTAURACION
  [ "$status" -eq 5 ]
  [ ! -f "$RESPALDO/restore-report.json" ]
}

@test "restore no escribe el .env en claro en el destino" {
  run python3 "$KIT/scripts/backup.py"
  [ "$status" -eq 0 ]
  RESPALDO="$(respaldo_reciente)"
  run python3 "$KIT/scripts/restore.py" "$RESPALDO" "$BATS_TEST_TMPDIR/destino" --confirmar CONFIRMAR_RESTAURACION
  [ "$status" -eq 0 ]
  [ ! -f "$BATS_TEST_TMPDIR/destino/.env" ]
}

@test "configure.py rechaza un BASIC_AUTH_HASH de ejemplo" {
  # Escenario real: alguien copia la plantilla y no cambia el hash.
  cp "$KIT/.env.example" "$KIT/.env"
  run python3 "$KIT/scripts/configure.py"
  [ "$status" -ne 0 ]
  [[ "$output" == *"REEMPLAZAR_HASH_BCRYPT"* ]]
}

@test "configure.py acepta un .env con un hash real" {
  printf 'BASIC_AUTH_USER=hefesto\nBASIC_AUTH_HASH=$2a$12$abcdefghijklmnopqrstuv\n' > "$KIT/.env"
  run python3 "$KIT/scripts/configure.py"
  [ "$status" -eq 0 ]
}

@test "el compose declara healthcheck en app y gateway" {
  run grep -c "healthcheck:" "$KIT/compose.yaml"
  [ "$output" -ge 2 ]
  run grep -c "condition: service_healthy" "$KIT/compose.yaml"
  [ "$output" -ge 1 ]
}
