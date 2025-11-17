# --- ¡CAMBIO! ---
# Usamos una imagen de Nginx más nueva (1.27)
# y "alpine-slim" que es más segura y ligera.
FROM nginx:1.27-alpine-slim

# Copiamos nuestra aplicación de una sola página (index.html)
COPY index.html /usr/share/nginx/html/index.html

# Copiamos el archivo de ayuda
COPY README_APP.md /usr/share/nginx/html/README_APP.md

# --- ¡NUEVA LÍNEA! Copia el logo. ---
COPY src/images/logo.png /usr/share/nginx/html/logo.png

# Copiamos nuestro archivo de configuración de Nginx (con cabeceras de seguridad)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
