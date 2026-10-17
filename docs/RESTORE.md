# Recuperación y traspaso
1. Preparar host con Docker/Compose; mantener origen intacto.
2. Ejecutar restore.py indicando backup confiable y carpeta nueva vacía. El destino recibe .env, compose y ops; no se reemplazan archivos existentes. Hashes detectan corrupción, no prueban origen confiable.
3. Dentro del destino ejecutar compose con override bootstrap, acceder por túnel, comprobar401 sin credencial y200 con ella.
4. Configurar dominio HTTPS a gateway8080, mantener app en red interna y probar herramientas usadas por cliente.
5. Si cambia responsable, generar otra contraseña/hash y recrear gateway con `docker compose up -d --force-recreate gateway`. Conservar respaldo anterior restringido; contiene hash antiguo.
6. Cambiar DNS/proxy y retirar origen tras aceptación. No hay base que sincronizar. Cookies, favoritos, descargas y almacenamiento local del navegador no se transfieren con este kit.

Para migrar a otro VPS, se requieren imágenes fijadas, configuración y capacidad de descarga de registry. El ZIP no incluye las imágenes Docker; no es instalador offline. Si se necesita recuperación sin Internet, exportar imágenes desde infraestructura de Hefesto y guardar junto al respaldo.

Odoo/WordPress: se puede enlazar este portal desde menú interno. No se proporciona módulo Odoo ni una API de conversión de archivos. Las funciones del navegador no se transforman automáticamente en endpoints REST.
