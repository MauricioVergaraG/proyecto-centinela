# services/frontend/Dockerfile
FROM nginx:1.25-alpine

# Copiamos nuestra aplicación de una sola página (index.html)
COPY index.html /usr/share/nginx/html/index.html

# --- ¡NUEVA LÍNEA! ---
# Copiamos el archivo de ayuda al mismo directorio
COPY README_APP.md /usr/share/nginx/html/README_APP.md

# Copiamos nuestro archivo de configuración de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
