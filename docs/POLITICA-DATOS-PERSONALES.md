# Uso responsable de las utilidades internas (Hefesto Studio)

Estado: vigente desde 2026-10-20. Responsable del tratamiento: el cliente que
opera el kit.

## 1. Enfoque: el riesgo esta en el uso, no en el almacenamiento

IT Tools **no almacena datos de forma persistente**: es un conjunto de
utilidades sin estado que operan sobre lo que el usuario pega en el navegador.
El kit no define volumenes de datos.

El riesgo real es distinto: un usuario puede **pegar datos personales de
terceros** (correos, RUT, numeros de telefono, claves) en una herramienta como
un validador o un codificador Base64, y ese dato queda en el **historial del
navegador** de quien lo uso.

## 2. Deberes (Ley 21.719) que aplican

- **Minimizacion**: usar las utilidades con datos sinteticos siempre que sea
  posible.
- **Finalidad**: este kit no es una herramienta de produccion ni de tratamiento
  de datos personales. Es un apoyo operativo.
- **No usar este kit como repositorio de datos**: lo que se pega no se guarda,
  pero queda en el navegador de quien lo pego.

## 3. Retencion

No aplica al kit: no persiste datos de usuario. El historial del navegador del
operador es responsabilidad del operador y de la politica del cliente.

## 4. Acceso

El gateway aplica **Basic Auth** con hash bcrypt (`BASIC_AUTH_HASH`).

- `scripts/configure.py` **rechaza** el valor de ejemplo (`REEMPLAZAR_HASH_BCRYPT`):
  con el, el acceso queda con una credencial conocida.
- Compartir la instancia implica compartir la credencial: **una instancia por
  cliente**.
- No hay RBAC: el control es de autenticacion, no de autorizacion.

## 5. Auditoria

- Los accesos al gateway quedan en el log de Caddy (`json-file`, con rotacion
  configurada en `compose.yaml`).
- El respaldo de configuracion genera `manifest.json` con checksum y deja
  registro de restauracion en `logs/restore.log` (sin valores de secretos).

## 6. El respaldo y el `.env`

El `.env` contiene el hash bcrypt del acceso: es un **factor de
autenticacion**. Por eso `scripts/backup.py` **no lo copia en claro**: escribe
solo `env.vars` (nombres de variables) y, si hay receptor `age`, `env.age`
(cifrado). Sin receptor, el respaldo sale sin el `.env` y el manifiesto lo
declara. Ver `docs/CONTRATO-RESPALDO.md`.

## 7. Seguridad del despliegue

- El gateway es la unica superficie expuesta: `app` vive en una red `backend`
  interna y no se publica ningun puerto al host.
- `security_opt: [no-new-privileges:true]` en ambos servicios.
- CSP con `default-src 'self'`, `object-src 'none'` y `frame-ancestors 'none'`
  en `ops/Caddyfile`.
- TLS lo termina el borde (Coolify/Traefik). El compose no publica `443`.
