#!/usr/bin/env bash
# ============================================================================
#  verify-m04.sh  -  Verificacion reproducible de P04 (arquitectura Web 3.0)
#
#  Lo invoca  ./scripts/verify-module.sh M04
#  Pasos: versiones -> build y pruebas de api-spring -> contenido del jar -> build de
#         frontend-angular -> pruebas del cliente -> validacion de openapi.yaml ->
#         PostgreSQL -> arranque de la API -> pruebas del contrato -> apagado de la API.
#  Cada paso deja su salida en docs/p04/evidencia/txt/ y se marca VERIFICADO,
#  NO_VERIFICADO o PENDIENTE. Termina con codigo 1 si hubo algun NO_VERIFICADO.
#
#  Variables opcionales:
#    DB_URL, DB_USER, DB_PASSWORD  conexion de la API (por omision, la base local de docker/)
#    API_PORT     puerto de la API (8081)
#    PSQL_CMD     comando psql (docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db)
#    CHROME_BIN   navegador Chromium para las pruebas de Angular; si no hay, quedan PENDIENTE
#    SKIP_FRONT=1 omite la compilacion y las pruebas del cliente Angular
#    SKIP_NAVEGADOR=1 omite el recorrido del cliente en navegador (Playwright)
#    WEB_PORT     puerto del servidor de desarrollo de Angular (4200)
# ============================================================================
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EVID="$ROOT/docs/p04/evidencia/txt"
PSQL_CMD="${PSQL_CMD:-docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db}"
API_PORT="${API_PORT:-8081}"
API_URL="http://localhost:$API_PORT"
WEB_PORT="${WEB_PORT:-4200}"
WEB_URL="http://localhost:$WEB_PORT"
# Valores del contenedor local declarado en docker/docker-compose.yml (datos ficticios de laboratorio)
export DB_URL="${DB_URL:-jdbc:postgresql://localhost:5436/huerto_db}"
export DB_USER="${DB_USER:-huerto_app}"
export DB_PASSWORD="${DB_PASSWORD:-huerto_dev}"
mkdir -p "$EVID"
FALLOS=0
RESUMEN=()
API_PID=""

paso()     { printf '\n== [M04] %s ==\n' "$1"; }
ok()       { echo "   VERIFICADO: $1";    RESUMEN+=("VERIFICADO    | $1"); }
falla()    { echo "   NO_VERIFICADO: $1"; RESUMEN+=("NO_VERIFICADO | $1"); FALLOS=$((FALLOS+1)); }
pendiente(){ echo "   PENDIENTE: $1";     RESUMEN+=("PENDIENTE     | $1"); }
salud()    { curl -s -o /dev/null -w '%{http_code}' "$API_URL/api/health" 2>/dev/null || true; }
apagar_api() {
  [ -z "$API_PID" ] && return 0
  kill "$API_PID" 2>/dev/null
  for i in $(seq 1 10); do [ "$(salud)" = "000" ] && break; sleep 1; done
  [ "$(salud)" != "000" ] && matar_puerto "$API_PORT"   # Windows: el proceso java no siempre recibe la senal
  API_PID=""
}
matar_puerto() { # matar_puerto <puerto> : detiene el proceso que escucha en ese puerto
  if command -v taskkill >/dev/null 2>&1; then
    WPID=$(netstat -ano 2>/dev/null | grep ":$1 " | grep LISTENING | awk '{print $5}' | head -1)
    [ -n "$WPID" ] && taskkill //PID "$WPID" //T //F >/dev/null 2>&1
  elif command -v lsof >/dev/null 2>&1; then
    lsof -ti "tcp:$1" | xargs -r kill 2>/dev/null
  fi
}
WEB_PID=""
apagar_web() {
  [ -z "$WEB_PID" ] && return 0
  kill "$WEB_PID" 2>/dev/null
  matar_puerto "$WEB_PORT"
  WEB_PID=""
}
trap 'apagar_web; apagar_api' EXIT

cd "$ROOT"

paso "Versiones del entorno"
{
  echo "fecha: $(date -Iseconds)"; echo "commit: $(git rev-parse --short HEAD 2>/dev/null)"
  java -version 2>&1; mvn -version 2>&1 | head -1
  echo "node: $(node --version 2>&1)"; echo "npm: $(npm --version 2>&1)"
  grep -E '"@angular/(core|cli)"' frontend-angular/package.json
  grep -A1 "<artifactId>spring-boot-starter-parent" api-spring/pom.xml | tail -1
} | tee "$EVID/00_versiones.txt"
java -version 2>&1 | grep -q '"11' && ok "Java 11 disponible" || falla "Se esperaba Java 11"
node --version 2>/dev/null | grep -q '^v18' && ok "Node 18 disponible" || falla "Se esperaba Node 18"

paso "Backend: compilacion, pruebas y empaquetado (mvn clean package)"
if mvn -B -f api-spring/pom.xml clean package > "$EVID/01_build_api.txt" 2>&1; then
  grep -E "Tests run:.*Skipped: [0-9]+$|BUILD" "$EVID/01_build_api.txt" | tail -2
  ok "api-spring compila con Java 11 y sus pruebas pasan"
else
  tail -30 "$EVID/01_build_api.txt"; falla "mvn clean package de api-spring (ver 01_build_api.txt)"
fi
cat api-spring/target/surefire-reports/*.txt > "$EVID/02_pruebas_api_unitarias.txt" 2>/dev/null || true

paso "Backend: contenido del jar"
unzip -l api-spring/target/api-spring.jar > "$EVID/03_jar_contenido.txt" 2>&1
grep -q "BOOT-INF/classes/mx/uv/dsw/huerto/api/lecturas/LecturaController.class" "$EVID/03_jar_contenido.txt" \
  && grep -q "BOOT-INF/lib/postgresql-" "$EVID/03_jar_contenido.txt" \
  && grep -q "BOOT-INF/lib/spring-jdbc-" "$EVID/03_jar_contenido.txt" \
  && grep -q "BOOT-INF/lib/springdoc-openapi-" "$EVID/03_jar_contenido.txt" \
  && ok "El jar contiene controladores, driver de PostgreSQL, Spring JDBC y springdoc" \
  || falla "Contenido del jar incompleto"
if grep -E "^(spring\.datasource\.(url|username|password)|huerto\.jwt\.secreto)=" api-spring/src/main/resources/application.properties \
   | grep -v -q '=\${'; then
  falla "application.properties tiene credenciales escritas"
else
  ok "application.properties toma conexion y secreto de variables de entorno"
fi

if [ "${SKIP_FRONT:-0}" = "1" ]; then
  pendiente "Cliente Angular: compilacion y pruebas omitidas (SKIP_FRONT=1)"
else
  paso "Frontend: compilacion de produccion (ng build)"
  if [ ! -d frontend-angular/node_modules ]; then
    (cd frontend-angular && npm ci > "$EVID/04_npm_ci.txt" 2>&1) || falla "npm ci (ver 04_npm_ci.txt)"
  fi
  if (cd frontend-angular && npx ng build > "$EVID/05_build_frontend.txt" 2>&1) && [ -f frontend-angular/dist/frontend-angular/index.html ]; then
    grep -E "Initial Total|Build at" "$EVID/05_build_frontend.txt"
    ok "frontend-angular compila y genera dist/frontend-angular"
  else
    tail -30 "$EVID/05_build_frontend.txt"; falla "ng build (ver 05_build_frontend.txt)"
  fi

  paso "Frontend: pruebas unitarias (Karma + Jasmine, Chromium sin ventana)"
  if [ -z "${CHROME_BIN:-}" ]; then
    # Chromium reciente separa el modo sin ventana en chrome-headless-shell (lo instala Playwright)
    CHROME_BIN=$(ls -d "$HOME"/AppData/Local/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell.exe 2>/dev/null | tail -1)
    [ -z "$CHROME_BIN" ] && CHROME_BIN=$(ls -d "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-*/headless_shell 2>/dev/null | tail -1)
    [ -z "$CHROME_BIN" ] && CHROME_BIN=$(command -v chromium chromium-browser google-chrome 2>/dev/null | head -1)
  fi
  if [ -n "${CHROME_BIN:-}" ] && [ -e "$CHROME_BIN" ]; then
    command -v cygpath >/dev/null 2>&1 && CHROME_BIN="$(cygpath -w "$CHROME_BIN")"
    export CHROME_BIN
    (cd frontend-angular && npx ng test --watch=false --browsers=ChromeHeadless > "$EVID/06_pruebas_frontend.tmp" 2>&1); SALIDA=$?
    # sin codigos de color ni lineas de progreso repetidas
    sed -e 's/\[[0-9;]*[A-Za-z]//g' "$EVID/06_pruebas_frontend.tmp" | grep -v -E "Executed [0-4] of" > "$EVID/06_pruebas_frontend.txt"
    rm -f "$EVID/06_pruebas_frontend.tmp"
    if [ "$SALIDA" -eq 0 ]; then
      grep -E "Executed [0-9]+ of [0-9]+.*SUCCESS" "$EVID/06_pruebas_frontend.txt" | tail -1
      ok "Las pruebas del cliente Angular pasan"
    else
      tail -20 "$EVID/06_pruebas_frontend.txt"; falla "ng test (ver 06_pruebas_frontend.txt)"
    fi
  else
    pendiente "Pruebas del cliente Angular: no hay navegador Chromium (definir CHROME_BIN)"
  fi
fi

paso "Contrato: validacion de docs/p04/openapi.yaml"
if python - > "$EVID/07_openapi_validacion.txt" 2>&1 <<'PY'
import yaml
from openapi_spec_validator import validate
spec = yaml.safe_load(open("docs/p04/openapi.yaml", encoding="utf-8"))
validate(spec)
print("docs/p04/openapi.yaml es un documento OpenAPI", spec["openapi"], "valido")
print("version del contrato:", spec["info"]["version"])
for ruta, ops in spec["paths"].items():
    for metodo, op in ops.items():
        print(f"  {metodo.upper():5} {ruta:22} {op['operationId']:20} respuestas: {', '.join(op['responses'])}")
print("esquemas:", ", ".join(spec["components"]["schemas"]))
PY
then cat "$EVID/07_openapi_validacion.txt"; ok "openapi.yaml es OpenAPI 3.0 valido"
else cat "$EVID/07_openapi_validacion.txt"; falla "openapi.yaml no valida (requiere: pip install openapi-spec-validator pyyaml)"
fi

paso "PostgreSQL: modelo y datos antes de las pruebas"
if $PSQL_CMD -v ON_ERROR_STOP=1 < sql/03_consultas_verificacion.sql > "$EVID/08_postgres_antes.txt" 2>&1; then
  ok "PostgreSQL responde y el modelo de 7 tablas existe"
else
  tail -5 "$EVID/08_postgres_antes.txt"; falla "No fue posible consultar PostgreSQL (revisa PSQL_CMD / docker compose)"
fi

paso "Arranque de la API en el puerto $API_PORT"
if [ "$(salud)" != "000" ]; then
  falla "El puerto $API_PORT ya esta ocupado; detenga ese proceso y repita"
else
  PORT="$API_PORT" java -jar api-spring/target/api-spring.jar > "$EVID/09_api_arranque.txt" 2>&1 &
  API_PID=$!
  for i in $(seq 1 40); do [ "$(salud)" = "200" ] && break; sleep 1; done
  grep -E "Tomcat started|JWT_SECRET" "$EVID/09_api_arranque.txt" | sed 's/^.*--- //'
  [ "$(salud)" = "200" ] && ok "La API arranca y /api/health responde 200" || falla "La API no respondio (ver 09_api_arranque.txt)"
fi

paso "Ruta de salud"
curl -s -i "$API_URL/api/health" > "$EVID/10_health.txt" 2>&1
grep -q '"db":"UP"' "$EVID/10_health.txt" && ok "/api/health reporta db=UP" || falla "/api/health no reporta db=UP"

paso "Pruebas del contrato contra la API en marcha (scripts/pruebas_api.py)"
if API_URL="$API_URL" PSQL_CMD="$PSQL_CMD" PYTHONIOENCODING=utf-8 PYTHONWARNINGS=ignore python scripts/pruebas_api.py > "$EVID/11_pruebas_api_salida.txt" 2>&1; then
  ok "pruebas_api.py termino sin casos NO_VERIFICADO"
else
  falla "pruebas_api.py reporto fallos (ver pruebas_api_resultados.txt)"
fi
cat "$EVID/pruebas_api_resultados.txt" 2>/dev/null
rm -f "$EVID/11_pruebas_api_salida.txt"   # repite pruebas_api.txt

paso "Recorrido del cliente Angular en navegador (Angular -> proxy -> API -> PostgreSQL)"
if [ "${SKIP_NAVEGADOR:-0}" = "1" ] || [ "${SKIP_FRONT:-0}" = "1" ]; then
  pendiente "Recorrido en navegador omitido (SKIP_NAVEGADOR=1)"
elif ! python -c "import playwright" 2>/dev/null; then
  pendiente "Recorrido en navegador: falta Playwright (pip install playwright && playwright install chromium)"
elif [ "$(curl -s -o /dev/null -w '%{http_code}' "$WEB_URL/" 2>/dev/null)" != "000" ]; then
  falla "El puerto $WEB_PORT ya esta ocupado; detenga ese proceso y repita"
else
  (cd frontend-angular && npx ng serve --port "$WEB_PORT" > "$EVID/11_ng_serve.txt" 2>&1) &
  WEB_PID=$!
  for i in $(seq 1 90); do
    [ "$(curl -s -o /dev/null -w '%{http_code}' "$WEB_URL/api/health" 2>/dev/null)" = "200" ] && break; sleep 1
  done
  if WEB_URL="$WEB_URL" API_URL="$API_URL" PSQL_CMD="$PSQL_CMD" PYTHONIOENCODING=utf-8 python scripts/recorrido_angular.py > "$EVID/11_recorrido_salida.txt" 2>&1; then
    ok "recorrido_angular.py termino sin casos NO_VERIFICADO"
  else
    tail -5 "$EVID/11_recorrido_salida.txt"; falla "recorrido_angular.py reporto fallos (ver recorrido_angular.txt)"
  fi
  grep -E "^[0-9]+ \||RESUMEN" "$EVID/recorrido_angular.txt" 2>/dev/null
  rm -f "$EVID/11_recorrido_salida.txt" "$EVID/11_ng_serve.txt"
  apagar_web
fi

paso "PostgreSQL despues de las pruebas (persistencia verificable)"
$PSQL_CMD < sql/03_consultas_verificacion.sql > "$EVID/12_postgres_despues.txt" 2>&1 \
  && grep -q "P04" "$EVID/12_postgres_despues.txt" \
  && ok "Las lecturas creadas por la API existen en PostgreSQL" || falla "Persistencia en PostgreSQL"

paso "Apagado de la API"
apagar_api
[ "$(salud)" = "000" ] && ok "La API se detuvo y el puerto $API_PORT quedo libre" || falla "La API sigue respondiendo"

paso "Anonimizando rutas locales en la evidencia"
EVID_DIR="$EVID" python scripts/anonimizar_evidencia.py || echo "   (aviso: no se pudo anonimizar; revisa manualmente)"

paso "Resumen"
{
  echo "verify-module.sh M04 - $(date -Iseconds) - commit $(git rev-parse --short HEAD 2>/dev/null)"
  printf '%s\n' "${RESUMEN[@]}"
  echo "Fallos: $FALLOS"
} | tee "$EVID/13_resumen.txt"
[ "$FALLOS" -eq 0 ] && echo "RESULTADO: VERIFICADO" || { echo "RESULTADO: NO_VERIFICADO ($FALLOS fallos)"; exit 1; }
