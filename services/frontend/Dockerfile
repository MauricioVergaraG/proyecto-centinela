# Autor: Mauricio Vergara
FROM node:20 AS build

WORKDIR /app
# copy only package.json (package-lock.json may be absent in the repo)
COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
