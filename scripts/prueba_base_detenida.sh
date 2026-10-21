#!/usr/bin/env bash
# ============================================================================
#  prueba_base_detenida.sh  -  P04/P05: comportamiento de la API cuando PostgreSQL no responde
#
#  Detiene el contenedor del proyecto (docker stop, sin borrar nada), consulta la API,
#  vuelve a arrancar el contenedor y comprueba que la API se recupera sola.
#  Con la base detenida, las lecturas, el cambio de estado de alertas y las anotaciones
#  deben responder 503 BASE_NO_DISPONIBLE sin guardar nada.
#  Salida: ${EVID_DIR:-docs/p05/evidencia/txt}/14_base_detenida.txt
#
#  No forma parte de verify-module.sh porque detiene la base que usan P02 y P03.
#  Variables: API_PORT (8081), CONTENEDOR (dsw-p02-huerto-db), EVID_DIR, DB_URL, DB_USER, DB_PASSWORD,
#             CLAVE_OBSERVADOR, CLAVE_RESPONSABLE (contrasenas ficticias de laboratorio, ver README)
# ============================================================================
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${EVID_DIR:-$ROOT/docs/p05/evidencia/txt}/14_base_detenida.txt"
API_PORT="${API_PORT:-8081}"
API="http://localhost:$API_PORT"
CONTENEDOR="${CONTENEDOR:-dsw-p02-huerto-db}"
CLAVE="${CLAVE_OBSERVADOR:-Observador#2026}"
CLAVE_RESP="${CLAVE_RESPONSABLE:-Responsable#2026}"
export DB_URL="${DB_URL:-jdbc:postgresql://localhost:5436/huerto_db}"
export DB_USER="${DB_USER:-huerto_app}"
export DB_PASSWORD="${DB_PASSWORD:-huerto_dev}"
cd "$ROOT"
mkdir -p "$(dirname "$OUT")"

codigo() { curl -s -o /dev/null -w '%{http_code}' "$@" 2>/dev/null || true; }
pedir()  { # pedir <titulo> <args de curl...>
  echo "--- $1"; shift
  curl -s -m 20 -w '\n[estado %{http_code}, %{time_total} s]\n' "$@"; echo
}
detener_api() {
  if command -v taskkill >/dev/null 2>&1; then
    WPID=$(netstat -ano 2>/dev/null | grep ":$API_PORT " | grep LISTENING | awk '{print $5}' | head -1)
    [ -n "$WPID" ] && taskkill //PID "$WPID" //T //F >/dev/null 2>&1
  else
    kill "$API_PID" 2>/dev/null
  fi
}
restaurar() { docker start "$CONTENEDOR" >/dev/null 2>&1; detener_api; }
trap restaurar EXIT

[ "$(codigo "$API/api/health")" != "000" ] && { echo "El puerto $API_PORT ya esta ocupado"; exit 2; }
PORT="$API_PORT" java -jar api-spring/target/api-spring.jar > /dev/null 2>&1 &
API_PID=$!
for i in $(seq 1 40); do [ "$(codigo "$API/api/health")" = "200" ] && break; sleep 1; done

{
  echo "prueba_base_detenida.sh - $(date -Iseconds)"
  echo
  echo "== 1. Base en marcha =="
  pedir "GET /api/health" "$API/api/health"
  TOKEN=$(curl -s -X POST "$API/api/auth/login" -H 'Content-Type: application/json' \
    -d "{\"usuario\":\"observador\",\"contrasena\":\"$CLAVE\"}" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')
  [ -n "$TOKEN" ] && echo "token obtenido para observador (no se imprime)" || echo "NO se obtuvo token"
  TOKEN_RESP=$(curl -s -X POST "$API/api/auth/login" -H 'Content-Type: application/json' \
    -d "{\"usuario\":\"responsable\",\"contrasena\":\"$CLAVE_RESP\"}" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')
  [ -n "$TOKEN_RESP" ] && echo "token obtenido para responsable (no se imprime)" || echo "NO se obtuvo token de responsable"
  echo
  echo "== 2. GET /api/zonas, /api/alertas, /api/anotaciones con token -> 200 (sin token -> 401) =="
  for ruta in /api/zonas /api/alertas /api/anotaciones; do
    echo "GET $ruta con token -> $(codigo -H "Authorization: Bearer $TOKEN" "$API$ruta")   sin token -> $(codigo "$API$ruta")"
  done
  echo
  echo "== 3. Usuario desconocido y contrasena incorrecta dan el mismo mensaje =="
  pedir "login de un usuario que no existe" -X POST "$API/api/auth/login" -H 'Content-Type: application/json' -d '{"usuario":"nadie","contrasena":"x"}'
  pedir "login de observador con contrasena incorrecta" -X POST "$API/api/auth/login" -H 'Content-Type: application/json' -d '{"usuario":"observador","contrasena":"x"}'
  echo "== 4. docker stop $CONTENEDOR =="
  docker stop "$CONTENEDOR" >/dev/null && echo "contenedor detenido (los datos quedan en su volumen)"
  echo
  pedir "GET /api/health" "$API/api/health"
  pedir "GET /api/sensores con token" -H "Authorization: Bearer $TOKEN" "$API/api/sensores"
  pedir "POST /api/lecturas con token" -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d '{"sensorId":2,"valor":25.5,"observacion":"[prueba] P05 base detenida"}' "$API/api/lecturas"
  pedir "PATCH /api/alertas/1 con token de responsable" -X PATCH -H "Authorization: Bearer $TOKEN_RESP" -H 'Content-Type: application/json' \
    -d '{"atendida":true}' "$API/api/alertas/1"
  pedir "POST /api/anotaciones con token" -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d '{"zonaId":1,"texto":"[prueba] P05 base detenida"}' "$API/api/anotaciones"
  pedir "POST /api/auth/login (no usa la base)" -o /dev/null -X POST "$API/api/auth/login" -H 'Content-Type: application/json' \
    -d "{\"usuario\":\"observador\",\"contrasena\":\"$CLAVE\"}"
  echo "== 5. docker start $CONTENEDOR =="
  docker start "$CONTENEDOR" >/dev/null && echo "contenedor en marcha"
  for i in $(seq 1 40); do [ "$(codigo "$API/api/health")" = "200" ] && break; sleep 1; done
  echo
  pedir "GET /api/health (la API se recupera sin reiniciarla)" "$API/api/health"
  echo "lecturas con la observacion de esta prueba en PostgreSQL (debe ser 0): $(docker exec "$CONTENEDOR" psql -U huerto_app -d huerto_db -At -c "SELECT count(*) FROM lectura WHERE observacion = '[prueba] P05 base detenida'")"
  echo "anotaciones con el texto de esta prueba en PostgreSQL (debe ser 0): $(docker exec "$CONTENEDOR" psql -U huerto_app -d huerto_db -At -c "SELECT count(*) FROM anotacion WHERE texto = '[prueba] P05 base detenida'")"
  echo "alerta 1 en PostgreSQL (atendida, atendida_por; sin cambio por esta prueba): $(docker exec "$CONTENEDOR" psql -U huerto_app -d huerto_db -At -c "SELECT atendida, coalesce(atendida_por, 'NULL') FROM alerta WHERE id = 1")"
} > "$OUT" 2>&1

cat "$OUT"
