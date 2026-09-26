#!/usr/bin/env bash
# ============================================================================
#  redeploy-tomcat.sh <war> [contexto]  -  Redespliega un WAR en Tomcat 9 de forma limpia.
#
#  En Windows, Tomcat mantiene bloqueados los jars de WEB-INF/lib mientras corre, asi que el
#  autoDeploy de un WAR nuevo puede quedarse con clases viejas. Este script detiene Tomcat,
#  borra el despliegue anterior (webapps/<ctx>, <ctx>.war y la cache de work/), copia el WAR
#  y vuelve a arrancar, esperando a que /<ctx>/health responda 200.
#
#  Requiere CATALINA_HOME. Ejemplo: CATALINA_HOME=/c/Tools/apache-tomcat-9.0.115 \
#                                    ./scripts/redeploy-tomcat.sh target/web2.war web2
# ============================================================================
set -u
WAR="${1:?uso: redeploy-tomcat.sh <ruta al WAR> [contexto]}"
CTX="${2:-$(basename "$WAR" .war)}"
: "${CATALINA_HOME:?Define CATALINA_HOME con la ruta de Tomcat 9}"
BASE_URL="${BASE_URL:-http://localhost:8080/$CTX}"

es_windows() { case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) return 0;; *) return 1;; esac; }
puerto_ocupado() { netstat -ano 2>/dev/null | grep -q ":8080 .*LISTEN"; }

echo "== Deteniendo Tomcat =="
if es_windows; then cmd //c "$(cygpath -w "$CATALINA_HOME/bin/shutdown.bat")" >/dev/null 2>&1
else "$CATALINA_HOME/bin/shutdown.sh" >/dev/null 2>&1; fi
for i in $(seq 1 20); do puerto_ocupado || break; sleep 2; done
if puerto_ocupado && es_windows; then
  pid=$(netstat -ano | grep ":8080 .*LISTEN" | head -1 | awk '{print $NF}')
  echo "   Tomcat no cerro a tiempo; se termina el proceso $pid"
  taskkill //PID "$pid" //F >/dev/null 2>&1; sleep 3
fi

echo "== Retirando despliegue anterior de /$CTX y copiando $WAR =="
rm -rf "$CATALINA_HOME/webapps/$CTX" "$CATALINA_HOME/webapps/$CTX.war" "$CATALINA_HOME/work/Catalina/localhost/$CTX"
cp "$WAR" "$CATALINA_HOME/webapps/$CTX.war"

echo "== Arrancando Tomcat =="
if es_windows; then cmd //c "$(cygpath -w "$CATALINA_HOME/bin/startup.bat")" >/dev/null 2>&1
else "$CATALINA_HOME/bin/startup.sh" >/dev/null 2>&1; fi
for i in $(seq 1 45); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 "$BASE_URL/health" 2>/dev/null || true)
  [ "$code" = "200" ] && { echo "   /$CTX/health -> 200"; sleep 2; exit 0; }
  sleep 3
done
echo "   /$CTX/health no respondio 200 (ultimo codigo: ${code:-sin respuesta})"; exit 1
