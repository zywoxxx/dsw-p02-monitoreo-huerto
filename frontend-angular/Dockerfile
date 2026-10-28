# Cliente Angular del PR09 servido por nginx. Dos etapas: Node compila el cliente; nginx sirve los
# estaticos y reenvia /api al contenedor de la API (ver nginx.conf). Se construye desde la raiz:
#   docker build -f frontend-angular/Dockerfile -t huerto-web .
FROM node:18.20-alpine AS build
WORKDIR /src
COPY frontend-angular/package.json frontend-angular/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend-angular/ .
RUN npx ng build --configuration production

FROM nginx:1.27-alpine
COPY frontend-angular/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/dist/frontend-angular /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=5s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
