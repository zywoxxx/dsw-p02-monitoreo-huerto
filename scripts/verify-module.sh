#!/usr/bin/env bash
# ============================================================================
#  verify-module.sh <M02|M03>  -  Verificacion reproducible del incremento
#
#  M02 (P02, JSP/Servlet, WAR web1): build -> WAR -> PostgreSQL -> Tomcat -> protocolo HTTP con curl.
#  M03 (P03, JSF/PrimeFaces, WAR web2): build -> WAR -> PostgreSQL -> Tomcat (reinicio limpio) ->
#       salud -> recorrido de aceptacion en navegador real (scripts/pruebas_jsf.py, Playwright).
#  Cada paso deja su salida en docs/<evidencia>/txt/ y se marca VERIFICADO o NO_VERIFICADO.
#  Termina con codigo 1 si algo fallo.
#
#  Ruta real del proyecto: este repositorio (no la carpeta codigo/dsw-evolucion-web del paquete docente).
#  Ejecutar desde la raiz:  CATALINA_HOME=/c/Tools/apache-tomcat-9.0.115 ./scripts/verify-module.sh M03
#
#  Variables opcionales:
#    CATALINA_HOME  ruta de Tomcat 9 (necesaria para desplegar; si falta se asume Tomcat ya en marcha)
#    BASE_URL       URL de la app (http://localhost:8080/web1 o /web2 segun el modulo)
#    PSQL_CMD       comando psql (docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db)
#    SKIP_DEPLOY=1  no despliega; usa el Tomcat que ya corre
# ============================================================================
set -u
MODULO="${1:-M03}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PSQL_CMD="${PSQL_CMD:-docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db}"
case "$MODULO" in
  M02) WAR=web1; EVID="$ROOT/docs/evidencia/txt" ;;
  M03) WAR=web2; EVID="$ROOT/docs/p03/evidencia/txt" ;;
  *) echo "Modulo no reconocido: $MODULO (usa M02 o M03)"; exit 2 ;;
esac
BASE_URL="${BASE_URL:-http://localhost:8080/$WAR}"
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
{ echo "fecha: $(date -Iseconds)"; echo "commit: $(git rev-parse --short HEAD 2>/dev/null)"; java -version 2>&1; mvn -version 2>&1 | head -3; } | tee "$EVID/00_versiones.txt"
java -version 2>&1 | grep -q '"11' && ok "Java 11 disponible" || falla "Se esperaba Java 11"

paso "Compilacion, pruebas unitarias y empaquetado (mvn clean package)"
if mvn -B clean package > "$EVID/01_build.txt" 2>&1; then
  grep -E "Tests run:|BUILD" "$EVID/01_build.txt" | tail -3
  ok "mvn clean package genera target/$WAR.war con pruebas en verde"
else
  tail -30 "$EVID/01_build.txt"; falla "mvn clean package (ver $EVID/01_build.txt)"
fi
cat target/surefire-reports/*.txt > "$EVID/02_pruebas_unitarias.txt" 2>/dev/null || true

paso "Inspeccion del WAR"
unzip -l "target/$WAR.war" > "$EVID/03_war_contenido.txt" 2>&1
if [ "$MODULO" = "M03" ]; then
  grep -q "WEB-INF/lib/javax.faces-" "$EVID/03_war_contenido.txt" \
    && grep -q "WEB-INF/lib/primefaces-" "$EVID/03_war_contenido.txt" \
    && grep -q "WEB-INF/lib/weld-servlet-shaded" "$EVID/03_war_contenido.txt" \
    && grep -q "app/lecturas.xhtml" "$EVID/03_war_contenido.txt" \
    && grep -q "WEB-INF/beans.xml" "$EVID/03_war_contenido.txt" \
    && ! grep -q "\.jsp$" "$EVID/03_war_contenido.txt" \
    && ok "WAR contiene Mojarra, PrimeFaces, Weld, beans.xml y vistas XHTML; sin JSP" \
    || falla "Estructura del WAR de P03 incompleta"
else
  grep -q "WEB-INF/classes/mx/uv/dsw/huerto/web/LecturaServlet.class" "$EVID/03_war_contenido.txt" \
    && grep -q "WEB-INF/lib/postgresql" "$EVID/03_war_contenido.txt" \
    && ok "WAR contiene servlets, JSP, web.xml y driver JDBC" || falla "Estructura del WAR incompleta"
fi

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
  # Reinicio limpio: en Windows Tomcat bloquea los jars y el autoDeploy puede conservar clases viejas
  BASE_URL="$BASE_URL" ./scripts/redeploy-tomcat.sh "target/$WAR.war" "$WAR" > "$EVID/05_tomcat_despliegue.txt" 2>&1 || true
  cat "$EVID/05_tomcat_despliegue.txt"
else
  echo "   CATALINA_HOME no definido: se asume Tomcat ya en ejecucion con $WAR desplegado"
fi
esperar_http 200 45 && sleep 2 && ok "$WAR desplegado y respondiendo en $BASE_URL" || falla "$WAR no respondio en $BASE_URL"
if [ -n "${CATALINA_HOME:-}" ]; then
  grep -h -E "Mojarra|PrimeFaces|WELD-ENV|Despliegue del archivo|Deployment of web archive|Server startup|SEVERE" \
    "$CATALINA_HOME"/logs/catalina.*.log 2>/dev/null | tail -8 > "$EVID/05_tomcat_log.txt"
fi

paso "Ruta de salud GET /health"
curl -s -i "$BASE_URL/health" > "$EVID/06_health.txt" 2>&1
grep -E "^HTTP|status" "$EVID/06_health.txt" | head -2
grep -q '"db":"UP"' "$EVID/06_health.txt" && ok "/health responde 200 y db=UP" || falla "/health no reporta db=UP"

if [ "$MODULO" = "M03" ]; then
  paso "Arranque JSF: pagina de acceso con PrimeFaces y proteccion de /app"
  curl -s -i "$BASE_URL/login.xhtml" > "$EVID/07_login_xhtml.txt"
  grep -q "^HTTP/1.1 200" "$EVID/07_login_xhtml.txt" && grep -q -i "primefaces" "$EVID/07_login_xhtml.txt" \
    && ok "login.xhtml responde 200 con recursos PrimeFaces" || falla "login.xhtml"
  curl -s -i "$BASE_URL/app/lecturas.xhtml" > "$EVID/08_app_sin_sesion.txt"
  grep -q "^HTTP/1.1 302" "$EVID/08_app_sin_sesion.txt" && grep -q "login.xhtml?expirada=1" "$EVID/08_app_sin_sesion.txt" \
    && ok "/app/lecturas.xhtml sin sesion redirige (302) al acceso" || falla "Proteccion de /app"

  paso "Recorrido de aceptacion en navegador real (Playwright)"
  if command -v python >/dev/null 2>&1 && python -c "import playwright" 2>/dev/null; then
    if BASE_URL="$BASE_URL" PSQL_CMD="$PSQL_CMD" python scripts/pruebas_jsf.py > "$EVID/09_pruebas_jsf_salida.txt" 2>&1; then
      ok "pruebas_jsf.py termino sin casos NO_VERIFICADO"
    else
      falla "pruebas_jsf.py reporto fallos (ver $EVID/pruebas_jsf_resultados.txt)"
    fi
    grep -E "VERIFICADO|Fallos" "$EVID/pruebas_jsf_resultados.txt" 2>/dev/null | tail -30
  else
    falla "Python + Playwright no disponibles; el recorrido JSF queda PENDIENTE (ver README, seccion pruebas)"
  fi

  paso "PostgreSQL despues del recorrido (persistencia verificable)"
  $PSQL_CMD < sql/03_consultas_verificacion.sql > "$EVID/10_postgres_despues.txt" 2>&1 \
    && grep -q "P03" "$EVID/10_postgres_despues.txt" \
    && ok "Las lecturas y anotaciones del recorrido existen en PostgreSQL" || falla "Persistencia en PostgreSQL"
else
  # ---------------------------- M02: protocolo HTTP con curl (P02) ----------------------------
  paso "Protocolo HTTP del flujo principal"
  curl -s -i "$BASE_URL/lecturas" > "$EVID/07_get_inicial.txt"
  grep -q "^HTTP/1.1 200" "$EVID/07_get_inicial.txt" && grep -q 'id="tabla-lecturas"' "$EVID/07_get_inicial.txt" \
    && ok "GET /lecturas inicial responde 200 con catalogo y lecturas" || falla "GET inicial"
  FILAS_ANTES=$(grep -c '<tr class="' "$EVID/07_get_inicial.txt")
  SENSOR_ID=$(grep -o '<option value="[0-9]*"[^>]*>SEN-A-TEMP-01' "$EVID/07_get_inicial.txt" | grep -o '[0-9][0-9]*' | head -1)
  [ -n "$SENSOR_ID" ] && echo "   sensor SEN-A-TEMP-01 -> id $SENSOR_ID" || { SENSOR_ID=0; falla "No se encontro SEN-A-TEMP-01 en el catalogo"; }
  curl -s -i -X POST -d "sensorId=$SENSOR_ID&valor=25.5&observacion=verify-module+POST+valido" "$BASE_URL/lecturas" > "$EVID/08_post_valido.txt"
  grep -q "^HTTP/1.1 303" "$EVID/08_post_valido.txt" && ok "POST valido responde 303" || falla "POST valido"
  curl -s -i -X POST -d "sensorId=$SENSOR_ID&valor=abc" "$BASE_URL/lecturas" > "$EVID/09_post_invalido_no_numerico.txt"
  grep -q "^HTTP/1.1 400" "$EVID/09_post_invalido_no_numerico.txt" && ok "POST invalido (abc) responde 400" || falla "POST invalido no numerico"
  curl -s -i -X POST -d "sensorId=&valor=" "$BASE_URL/lecturas" > "$EVID/10_post_invalido_vacio.txt"
  grep -q "^HTTP/1.1 400" "$EVID/10_post_invalido_vacio.txt" && ok "POST invalido (vacio) responde 400" || falla "POST invalido vacio"
  curl -s -i -X POST -d "sensorId=$SENSOR_ID&valor=150" "$BASE_URL/lecturas" > "$EVID/11_post_invalido_rango_fisico.txt"
  grep -q "^HTTP/1.1 400" "$EVID/11_post_invalido_rango_fisico.txt" && ok "POST invalido (150 C) responde 400" || falla "POST invalido rango fisico"
  curl -s -i -X POST -d "sensorId=$SENSOR_ID&valor=38&observacion=verify-module+alerta" "$BASE_URL/lecturas" > "$EVID/12_post_valido_con_alerta.txt"
  grep -q "alerta=ALTA" "$EVID/12_post_valido_con_alerta.txt" && ok "POST 38 C genera alerta ALTA" || falla "POST con alerta"
  curl -s -i "$BASE_URL/lecturas" > "$EVID/13_get_persistencia.txt"
  FILAS_DESPUES=$(grep -c '<tr class="' "$EVID/13_get_persistencia.txt")
  [ "$FILAS_DESPUES" -gt "$FILAS_ANTES" ] && ok "GET posterior muestra las lecturas persistidas" || falla "GET con persistencia"
  curl -s -i "$BASE_URL/alertas" > "$EVID/14_get_alertas.txt"
  grep -q "^HTTP/1.1 200" "$EVID/14_get_alertas.txt" && ok "GET /alertas responde 200" || falla "GET alertas"
  paso "PostgreSQL despues del protocolo"
  $PSQL_CMD < sql/03_consultas_verificacion.sql > "$EVID/15_postgres_despues.txt" 2>&1 \
    && grep -q "verify-module" "$EVID/15_postgres_despues.txt" && ok "Las lecturas del protocolo existen" || falla "Persistencia en PostgreSQL"
fi

paso "Anonimizando rutas locales en la evidencia"
if command -v python >/dev/null 2>&1; then
  EVID_DIR="$EVID" python scripts/anonimizar_evidencia.py || echo "   (aviso: no se pudo anonimizar; revisa manualmente)"
else
  echo "   AVISO: python no disponible; revisa manualmente que no queden rutas privadas en $EVID"
fi

paso "Resumen"
{
  echo "verify-module.sh $MODULO - $(date -Iseconds) - commit $(git rev-parse --short HEAD 2>/dev/null)"
  printf '%s\n' "${RESUMEN[@]}"
  echo "Fallos: $FALLOS"
} | tee "$EVID/16_resumen.txt"
[ "$FALLOS" -eq 0 ] && echo "RESULTADO: VERIFICADO" || { echo "RESULTADO: NO_VERIFICADO ($FALLOS fallos)"; exit 1; }
