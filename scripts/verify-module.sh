#!/usr/bin/env bash
# ============================================================================
#  verify-module.sh M02  -  Verificacion reproducible del incremento P02
#
#  Pasos: versiones -> build + pruebas -> inspeccion del WAR -> PostgreSQL ->
#         despliegue en Tomcat -> ruta de salud -> protocolo HTTP (GET inicial,
#         POST valido, POST invalido x3, POST con alerta, GET con persistencia,
#         GET alertas) -> persistencia en PostgreSQL -> anonimizacion de rutas.
#  Cada paso deja su salida en docs/evidencia/txt/ y se marca VERIFICADO o
#  NO_VERIFICADO. El script termina con codigo 1 si algo fallo.
#
#  Variables opcionales (todas con valor por defecto de laboratorio):
#    CATALINA_HOME  ruta de Tomcat 9        (p. ej. /c/Tools/apache-tomcat-9.0.115)
#    BASE_URL       URL de la app           (http://localhost:8080/web1)
#    PSQL_CMD       comando psql            (docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db)
#    SKIP_DEPLOY=1  no copia el WAR ni arranca Tomcat (usa el que ya corre)
# ============================================================================
set -u
MODULO="${1:-M02}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EVID="$ROOT/docs/evidencia/txt"
BASE_URL="${BASE_URL:-http://localhost:8080/web1}"
PSQL_CMD="${PSQL_CMD:-docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db}"
mkdir -p "$EVID"
FALLOS=0
RESUMEN=()

paso() { printf '\n== [%s] %s ==\n' "$MODULO" "$1"; }
ok()   { echo "   VERIFICADO: $1";    RESUMEN+=("VERIFICADO    | $1"); }
falla(){ echo "   NO_VERIFICADO: $1"; RESUMEN+=("NO_VERIFICADO | $1"); FALLOS=$((FALLOS+1)); }
esperar_http() { # esperar_http <codigo> <intentos>
  for i in $(seq 1 "$2"); do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/health" 2>/dev/null || true)
    [ "$code" = "$1" ] && return 0; sleep 2
  done; return 1
}

cd "$ROOT"

paso "Versiones del entorno"
{ echo "fecha: $(date -Iseconds)"; java -version 2>&1; mvn -version 2>&1 | head -3; } | tee "$EVID/00_versiones.txt"
java -version 2>&1 | grep -q '"11' && ok "Java 11 disponible" || falla "Se esperaba Java 11"

paso "Compilacion, pruebas unitarias y empaquetado (mvn clean package)"
if mvn -B clean package > "$EVID/01_build.txt" 2>&1; then
  grep -E "Tests run:|BUILD" "$EVID/01_build.txt" | tail -3
  ok "mvn clean package genera target/web1.war con pruebas en verde"
else
  tail -30 "$EVID/01_build.txt"; falla "mvn clean package (ver docs/evidencia/txt/01_build.txt)"
fi
cp target/surefire-reports/*.txt "$EVID/02_pruebas_unitarias.txt" 2>/dev/null || true

paso "Inspeccion del WAR"
unzip -l target/web1.war > "$EVID/03_war_contenido.txt" 2>&1
grep -q "WEB-INF/classes/mx/uv/dsw/huerto/web/LecturaServlet.class" "$EVID/03_war_contenido.txt" \
  && grep -q "WEB-INF/lib/postgresql" "$EVID/03_war_contenido.txt" \
  && ok "WAR contiene servlets, JSP, web.xml y driver JDBC" \
  || falla "Estructura del WAR incompleta"

paso "PostgreSQL: esquema, semilla y consultas de verificacion"
if $PSQL_CMD -v ON_ERROR_STOP=1 < sql/03_consultas_verificacion.sql > "$EVID/04_postgres_verificacion.txt" 2>&1; then
  head -12 "$EVID/04_postgres_verificacion.txt"
  ok "PostgreSQL responde y el modelo de 7 tablas existe"
else
  cat "$EVID/04_postgres_verificacion.txt"; falla "No fue posible consultar PostgreSQL (revisa PSQL_CMD / docker compose)"
fi

paso "Despliegue en Tomcat 9"
if [ "${SKIP_DEPLOY:-0}" = "1" ]; then
  echo "   SKIP_DEPLOY=1: se usa el Tomcat que ya esta en ejecucion"
elif [ -n "${CATALINA_HOME:-}" ] && [ -d "$CATALINA_HOME/webapps" ]; then
  if curl -s -o /dev/null "$BASE_URL/health" 2>/dev/null; then
    echo "   Tomcat activo: se retira web1 y se espera a que Tomcat lo repliegue (autoDeploy)"
    rm -rf "$CATALINA_HOME/webapps/web1.war" "$CATALINA_HOME/webapps/web1"
    esperar_http 404 30 || echo "   (aviso: el contexto anterior sigue respondiendo)"
    cp target/web1.war "$CATALINA_HOME/webapps/"
    echo "   web1.war copiado; esperando el nuevo despliegue"
  else
    rm -rf "$CATALINA_HOME/webapps/web1.war" "$CATALINA_HOME/webapps/web1"
    cp target/web1.war "$CATALINA_HOME/webapps/"
    echo "   Tomcat no responde: se arranca con $CATALINA_HOME/bin/startup"
    case "$(uname -s)" in
      MINGW*|MSYS*|CYGWIN*) cmd //c "$(cygpath -w "$CATALINA_HOME/bin/startup.bat")" >/dev/null 2>&1 ;;
      *) "$CATALINA_HOME/bin/startup.sh" >/dev/null 2>&1 ;;
    esac
  fi
else
  echo "   CATALINA_HOME no definido: se asume Tomcat ya en ejecucion con web1 desplegado"
fi
esperar_http 200 45 && sleep 2 && ok "web1 desplegado y respondiendo en $BASE_URL" || falla "web1 no respondio en $BASE_URL"
if [ -n "${CATALINA_HOME:-}" ]; then
  grep -h -E "Despliegue del archivo|Deploying web application archive|Deployment of web archive|Server startup|SEVERE" \
    "$CATALINA_HOME"/logs/catalina.*.log 2>/dev/null | tail -6 > "$EVID/05_tomcat_log.txt"
fi

paso "Ruta de salud GET /health"
curl -s -i "$BASE_URL/health" > "$EVID/06_health.txt" 2>&1
grep -E "^HTTP|status" "$EVID/06_health.txt" | head -2
grep -q '"db":"UP"' "$EVID/06_health.txt" && ok "/health responde 200 y db=UP" || falla "/health no reporta db=UP"

paso "Protocolo HTTP del flujo principal"
# 1) GET inicial
curl -s -i "$BASE_URL/lecturas" > "$EVID/07_get_inicial.txt"
grep -q "^HTTP/1.1 200" "$EVID/07_get_inicial.txt" && grep -q 'id="tabla-lecturas"' "$EVID/07_get_inicial.txt" \
  && ok "GET /lecturas inicial responde 200 con catalogo y lecturas" || falla "GET inicial"
FILAS_ANTES=$(grep -c '<tr class="' "$EVID/07_get_inicial.txt")
# id del sensor de temperatura SEN-A-TEMP-01 (rango fisico [-10,60], umbral [15,32]) tomado del catalogo
SENSOR_ID=$(grep -o '<option value="[0-9]*"[^>]*>SEN-A-TEMP-01' "$EVID/07_get_inicial.txt" | grep -o '[0-9][0-9]*' | head -1)
[ -n "$SENSOR_ID" ] && echo "   sensor SEN-A-TEMP-01 -> id $SENSOR_ID" || { SENSOR_ID=0; falla "No se encontro SEN-A-TEMP-01 en el catalogo"; }

# 2) POST valido (valor en rango, sin alerta)
curl -s -i -X POST -d "sensorId=$SENSOR_ID&valor=25.5&observacion=verify-module+POST+valido" "$BASE_URL/lecturas" > "$EVID/08_post_valido.txt"
grep -q "^HTTP/1.1 303" "$EVID/08_post_valido.txt" && grep -q "Location: .*creada=" "$EVID/08_post_valido.txt" \
  && ok "POST valido responde 303 y redirige a la lectura creada" || falla "POST valido"

# 3) POST invalido: valor no numerico -> 400 con mensaje
curl -s -i -X POST -d "sensorId=$SENSOR_ID&valor=abc" "$BASE_URL/lecturas" > "$EVID/09_post_invalido_no_numerico.txt"
grep -q "^HTTP/1.1 400" "$EVID/09_post_invalido_no_numerico.txt" && grep -q "debe ser numerico" "$EVID/09_post_invalido_no_numerico.txt" \
  && ok "POST invalido (valor abc) responde 400 con mensaje de validacion" || falla "POST invalido no numerico"

# 4) POST invalido: campos vacios
curl -s -i -X POST -d "sensorId=&valor=" "$BASE_URL/lecturas" > "$EVID/10_post_invalido_vacio.txt"
grep -q "^HTTP/1.1 400" "$EVID/10_post_invalido_vacio.txt" && grep -q "Debe seleccionar un sensor" "$EVID/10_post_invalido_vacio.txt" \
  && ok "POST invalido (vacio) responde 400 con dos errores" || falla "POST invalido vacio"

# 5) POST invalido: fuera del rango fisico
curl -s -i -X POST -d "sensorId=$SENSOR_ID&valor=150" "$BASE_URL/lecturas" > "$EVID/11_post_invalido_rango_fisico.txt"
grep -q "^HTTP/1.1 400" "$EVID/11_post_invalido_rango_fisico.txt" && grep -q "fuera del rango fisico" "$EVID/11_post_invalido_rango_fisico.txt" \
  && ok "POST invalido (150 C) responde 400 por rango fisico" || falla "POST invalido rango fisico"

# 6) POST valido fuera de umbral -> alerta ALTA
curl -s -i -X POST -d "sensorId=$SENSOR_ID&valor=38&observacion=verify-module+alerta" "$BASE_URL/lecturas" > "$EVID/12_post_valido_con_alerta.txt"
grep -q "^HTTP/1.1 303" "$EVID/12_post_valido_con_alerta.txt" && grep -q "alerta=ALTA" "$EVID/12_post_valido_con_alerta.txt" \
  && ok "POST 38 C responde 303 y genera alerta ALTA" || falla "POST con alerta"

# 7) GET con persistencia: aparecen las lecturas nuevas
curl -s -i "$BASE_URL/lecturas" > "$EVID/13_get_persistencia.txt"
FILAS_DESPUES=$(grep -c '<tr class="' "$EVID/13_get_persistencia.txt")
grep -q "verify-module POST valido" "$EVID/13_get_persistencia.txt" && [ "$FILAS_DESPUES" -gt "$FILAS_ANTES" ] \
  && ok "GET posterior muestra las lecturas persistidas ($FILAS_ANTES -> $FILAS_DESPUES filas)" || falla "GET con persistencia"

# 8) GET alertas
curl -s -i "$BASE_URL/alertas" > "$EVID/14_get_alertas.txt"
grep -q "^HTTP/1.1 200" "$EVID/14_get_alertas.txt" && grep -q "etiqueta-ALTA" "$EVID/14_get_alertas.txt" \
  && ok "GET /alertas lista la alerta generada" || falla "GET alertas"

paso "PostgreSQL despues del protocolo (persistencia verificable)"
$PSQL_CMD < sql/03_consultas_verificacion.sql > "$EVID/15_postgres_despues.txt" 2>&1 \
  && grep -q "verify-module" "$EVID/15_postgres_despues.txt" \
  && ok "Las lecturas del protocolo existen en la tabla lectura" || falla "Persistencia en PostgreSQL"

paso "Anonimizando rutas locales en la evidencia"
# La guia P02 prohibe rutas privadas: se sustituyen repositorio, Tomcat y HOME por marcadores.
if command -v python >/dev/null 2>&1; then
  python scripts/anonimizar_evidencia.py || echo "   (aviso: no se pudo anonimizar; revisa manualmente)"
else
  echo "   AVISO: python no disponible; revisa manualmente que no queden rutas privadas en docs/evidencia/txt"
fi

paso "Resumen"
{
  echo "verify-module.sh $MODULO - $(date -Iseconds)"
  printf '%s\n' "${RESUMEN[@]}"
  echo "Fallos: $FALLOS"
} | tee "$EVID/16_resumen.txt"
[ "$FALLOS" -eq 0 ] && echo "RESULTADO: VERIFICADO" || { echo "RESULTADO: NO_VERIFICADO ($FALLOS fallos)"; exit 1; }
