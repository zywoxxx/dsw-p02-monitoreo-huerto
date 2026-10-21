#!/usr/bin/env bash
# ============================================================================
#  demo_p05.sh  -  Levanta la aplicacion completa en localhost para mostrarla
#
#  ./scripts/demo_p05.sh         arranca PostgreSQL (contenedor), la API (8081) y el cliente (4200),
#                                espera a que respondan y abre el navegador
#  ./scripts/demo_p05.sh stop    detiene la API y el cliente (la base sigue; no se borra nada)
#
#  Usuarios ficticios de laboratorio: observador / Observador#2026 (captura lecturas),
#  responsable / Responsable#2026 (atiende alertas), coordinacion / Coordinacion#2026 (consulta).
#  Variables opcionales: API_PORT (8081), WEB_PORT (4200), DB_URL, DB_USER, DB_PASSWORD, JWT_SECRET.
# ============================================================================
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_PORT="${API_PORT:-8081}"
WEB_PORT="${WEB_PORT:-4200}"
REGISTROS="${TEMP:-/tmp}/huerto-demo"
export DB_URL="${DB_URL:-jdbc:postgresql://localhost:5436/huerto_db}"
export DB_USER="${DB_USER:-huerto_app}"
export DB_PASSWORD="${DB_PASSWORD:-huerto_dev}"
export PORT="$API_PORT"
cd "$ROOT"
mkdir -p "$REGISTROS"

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    [ -d /c/Tools/node-v18.20.8-win-x64 ] && export PATH="/c/Tools/node-v18.20.8-win-x64:$PATH"
    [ -d "/c/Program Files/Docker/Docker/resources/bin" ] && export PATH="$PATH:/c/Program Files/Docker/Docker/resources/bin"
    abrir() { cmd //c start "" "$1" >/dev/null 2>&1; }
    matar_puerto() {
      for pid in $(netstat -ano 2>/dev/null | grep ":$1 " | grep LISTENING | awk '{print $5}' | sort -u); do
        taskkill //PID "$pid" //T //F >/dev/null 2>&1
      done
    }
    ;;
  Darwin) abrir() { open "$1"; }; matar_puerto() { lsof -ti "tcp:$1" | xargs -r kill; } ;;
  *)      abrir() { xdg-open "$1" >/dev/null 2>&1 || true; }; matar_puerto() { lsof -ti "tcp:$1" | xargs -r kill; } ;;
esac
codigo() { curl -s -o /dev/null -w '%{http_code}' "$1" 2>/dev/null || true; }

if [ "${1:-}" = "stop" ]; then
  matar_puerto "$WEB_PORT"; matar_puerto "$API_PORT"
  echo "API y cliente detenidos. La base de datos sigue en marcha (docker compose ... stop para detenerla)."
  exit 0
fi

echo "== Base de datos =="
docker compose -f docker/docker-compose.yml up -d >/dev/null 2>&1 || true
for i in $(seq 1 30); do
  [ "$(docker inspect -f '{{.State.Health.Status}}' dsw-p02-huerto-db 2>/dev/null)" = "healthy" ] && break; sleep 2
done
docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db -v ON_ERROR_STOP=1 < sql/04_p05_atencion_alerta.sql >/dev/null \
  && echo "   PostgreSQL en marcha; migracion de P05 aplicada (idempotente)" || { echo "   PostgreSQL no responde"; exit 1; }

echo "== API Spring Boot (puerto $API_PORT) =="
if [ "$(codigo "http://localhost:$API_PORT/api/health")" = "200" ]; then
  echo "   ya habia una API respondiendo; se reutiliza"
else
  [ -f api-spring/target/api-spring.jar ] || { echo "   compilando..."; mvn -B -q -f api-spring/pom.xml -DskipTests clean package; }
  nohup java -jar api-spring/target/api-spring.jar > "$REGISTROS/api.log" 2>&1 &
  for i in $(seq 1 60); do [ "$(codigo "http://localhost:$API_PORT/api/health")" = "200" ] && break; sleep 1; done
  [ "$(codigo "http://localhost:$API_PORT/api/health")" = "200" ] && echo "   API arriba (registro: $REGISTROS/api.log)" || { tail -5 "$REGISTROS/api.log"; exit 1; }
fi

echo "== Cliente Angular (puerto $WEB_PORT) =="
if [ "$(codigo "http://localhost:$WEB_PORT/")" = "200" ]; then
  echo "   ya habia un cliente respondiendo; se reutiliza"
else
  [ -d frontend-angular/node_modules ] || (cd frontend-angular && npm ci >/dev/null 2>&1)
  (cd frontend-angular && nohup npx ng serve --port "$WEB_PORT" > "$REGISTROS/web.log" 2>&1 &)
  for i in $(seq 1 120); do [ "$(codigo "http://localhost:$WEB_PORT/api/health")" = "200" ] && break; sleep 1; done
  [ "$(codigo "http://localhost:$WEB_PORT/api/health")" = "200" ] && echo "   cliente arriba (registro: $REGISTROS/web.log)" || { tail -5 "$REGISTROS/web.log"; exit 1; }
fi
# la primera peticion que pasa por el proxy de desarrollo tarda un poco; se calienta aqui
curl -s -o /dev/null -X POST "http://localhost:$WEB_PORT/api/auth/login" -H 'Content-Type: application/json' -d '{"usuario":"x","contrasena":"x"}'

cat <<FIN

Listo. Para la demostracion:
  Cliente Angular    http://localhost:$WEB_PORT          (observador registra lecturas; responsable atiende alertas; coordinacion consulta)
  Salud de la API    http://localhost:$API_PORT/api/health
  Swagger (springdoc) http://localhost:$API_PORT/swagger-ui.html
  Contrato escrito   docs/p04/openapi.yaml
Detener:  ./scripts/demo_p05.sh stop
FIN
abrir "http://localhost:$WEB_PORT"
abrir "http://localhost:$API_PORT/swagger-ui.html"
