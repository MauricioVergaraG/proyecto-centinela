# --- Etapa 1: Construcción (Build) ---
# (Asumo que usas Node 20 y Alpine, como en el pipeline)
FROM node:20-alpine AS build

WORKDIR /app

# Copia el package.json y package-lock.json (si existe)
COPY package.json package-lock.json* ./

# Instala dependencias: usa 'npm ci' si existe package-lock.json, si no cae
# de forma segura a 'npm install' (útil para entornos donde aún no se creó
# el package-lock.json).
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copia el resto del código fuente
COPY . .

# Construye la aplicación
RUN npm run build

# --- Etapa 2: Producción (Runtime) ---
# (Usamos una imagen 'slim' más segura)
FROM nginx:1.27-alpine-slim

# 1. Copia los archivos de la app construidos desde la etapa 'build'
COPY --from=build /app/dist /usr/share/nginx/html

# --- ¡AQUÍ ESTÁ EL CAMBIO! ---
# 2. Copia nuestra nueva configuración de Nginx (con cabeceras de seguridad)
#    y reemplaza la configuración por defecto.
# Al construir con contexto 'services/frontend' el archivo 'nginx.conf' está
# en la raíz del contexto, por lo que copiamos directamente desde './nginx.conf'
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expone el puerto 80
EXPOSE 80

# Comando por defecto para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
