# Validación en infraestructura
- docker compose config --quiet; confirmar hashes preservados (no imprimir config pública).
- Arranque Caddy valida Caddyfile; sintaxis no ejecutada localmente por falta de binario/Docker.
- Petición anónima página/recurso devuelve401; credencial correcta permite200, incorrecta401.
- Solo gateway accesible por dominio; no exposición directa a app ni puerto8080 externo sinTLS.
- Probar formateo JSON con ejemplo, conversión de fecha, hash de texto ficticio y copia/descarga.
- Revisar consola CSP y Network: recursos externos bloqueados; inventariar herramientas limitadas.
- No pegar tokens/APIkeys reales; revisar persistencia en almacenamiento local y limpiar ensayo.
- Rotar contraseña, recrear gateway y probar desde ventana nueva.
- Backup y restore a directorio vacío; repetir prueba de acceso.
- Escaneo de imágenes/dependencias y actualización en copia privada antes de abrir producción.

Comprobado localmente: YAML, Python/shell, configuración sin sobrescritura, round-trip backup/restore de archivos sintéticos y rechazo de hash alterado. No se probó UI ni servidor real.
