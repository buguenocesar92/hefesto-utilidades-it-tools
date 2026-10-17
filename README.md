# Hefesto Utilidades · IT-Tools + Caddy

Portal de utilidades técnicas: formatos JSON/YAML, fechas, hashes, texto y otras herramientas del catálogo nativo. Basado en el fork sharevb/it-tools2026.9.27, publicado más recientemente que la última release del repositorio original de CorentinTh. Se conserva interfaz y atribución del producto.

## Arquitectura
Aplicación web estática en contenedor Nginx sin privilegios; gateway Caddy con Basic Auth. TLS termina en proxy Coolify. Solo el gateway se conecta al proxy; app está en red interna y no publica puertos. No hay DB, Supabase, cuentas en la aplicación ni sincronización de datos entre dispositivos.

La política CSP restringe fetch/WebSocket a mismo origen y carga de recursos a orígenes limitados. Herramientas que dependan de APIs, CDN o recursos externos pueden no funcionar con esta política. No abrir globalmente connect-src para arreglarlas: evaluar cada origen. No se incluyen bridges TCP/UDP ni proxies de red.

Esto no certifica funcionamiento offline de todo el catálogo ni ausencia absoluta de tráfico externo del navegador. Revisar pestaña Network y consola durante aceptación. Favoritos/preferencias/resultados pueden permanecer en navegador: no forman parte de respaldo servidor. Evitar datos reales secretos durante pruebas y limpiar almacenamiento local al usar equipos compartidos.

## Instalación privada
Requisitos: Docker + Compose v2, Python3.11+ y proxy HTTPS. Inicio orientativo: 1CPU/512MB para dos contenedores, medir navegación y concurrencia.

1. `python3 scripts/configure.py`. .env0600, no versionado.
2. Generar hash de contraseña de forma interactiva:
```
docker run --rm -it caddy:2-alpine@sha256:d8542f48d34a9cf4e4c11a478865229840e87e4c96ea3f439101f31a5d35f75f caddy hash-password --algorithm bcrypt --bcrypt-cost 12
```
3. Copiar solo hash a BASIC_AUTH_HASH manteniendo comillas simples en .env (protegen signos $). Usuario de3–48 caracteres alfanuméricos, _ o -. No usar contraseña de ejemplo ni valor plano. Caddy rechaza arranque sin hash válido.
4. `docker compose -f compose.yaml -f compose.bootstrap.yaml up -d`. Abrir http://localhost:8107 o túnel `ssh -L 8107:127.0.0.1:8107 usuario@servidor`. Debe solicitar credencial antes de servir página/recursos. Probar examples/datos-demo.json.
5. Verificar acceso anónimo con `curl -I http://localhost:8107`:401. Prueba autenticada `curl -u hefesto -I http://localhost:8107` solicita contraseña; espera200.
6. Detener: `docker compose -f compose.yaml -f compose.bootstrap.yaml down`. Importar compose.yaml, ops y variables en Coolify. Asociar dominio HTTPS a **gateway:8080**, nunca a app.
7. No incluir override bootstrap en publicación. No publicar puerto de app ni agregar app a la red del proxy. En Coolify comprobar que solo gateway recibe dominio y ruta externa. Caddy no gestiona certificados aquí; HTTPS y redirección HTTP se configuran en proxy exterior.
8. Si pega variables en interfaz Coolify, usar hash literal sin comillas de .env y comprobar signos $ intactos. No compartir salida de compose config (incluye hash).

Basic Auth ofrece una cuenta de acceso, no roles ni MFA. El navegador puede conservar la credencial y recursos ya descargados: cerrar ventana privada/revocar contraseña no borra datos ya presentes en dispositivo. No hay panel de usuarios ni logout de aplicación añadido. Para equipo con identidades individuales, implementar proveedor de identidad/gateway como proyecto separado.

## Operación y portabilidad
`python3 scripts/backup.py` copia configuración y hash; no necesita detener contenedores porque no hay base/archivos de usuarios en servidor. No editar config durante copia. Datos del navegador requieren exportación/copia propia cuando la herramienta la permita.

`python3 scripts/restore.py /ruta/respaldo /ruta/destino-nuevo` restaura solo archivos previstos, verifica hashes y exige destino vacío. Ver docs/RESTORE.md. Cifrar respaldos y guardar fuera del servidor.

Imágenes fijadas por digest. No se conectan Odoo, APIs externas ni cuentas reales. Estado: scripts/configuración revisados localmente; no se ejecutó Docker/Caddy ni interfaz en este entorno. Completar docs/ACCEPTANCE.md antes de producción.
