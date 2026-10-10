#!/usr/bin/env bash
# ============================================================================
#  cleanup.sh  -  Limpieza de recursos locales (P02, P03 y P04)
#
#  Sin argumentos : borra SOLO las lecturas/alertas creadas por las pruebas
#                   (origen = 'manual') y las carpetas generadas: target/,
#                   api-spring/target/, frontend-angular/dist/ y .angular/.
#                   Conserva semilla y node_modules.
#  --all          : ademas detiene Tomcat (si CATALINA_HOME esta definido) y
#                   elimina el contenedor y el volumen de PostgreSQL.
#  Solo afecta recursos declarados en este repositorio; nunca infraestructura ajena.
# ============================================================================
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PSQL_CMD="${PSQL_CMD:-docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db}"
cd "$ROOT"

echo "== Borrando lecturas y alertas de prueba (origen = manual) =="
$PSQL_CMD < sql/99_cleanup.sql || echo "   (PostgreSQL no disponible; se omite)"

echo "== Eliminando carpetas generadas (target/, api-spring/target/, frontend-angular/dist/) =="
rm -rf target api-spring/target frontend-angular/dist frontend-angular/.angular

# La API de P04 no debe quedar corriendo
if curl -s -o /dev/null "http://localhost:${API_PORT:-8081}/api/health" 2>/dev/null; then
  echo "   AVISO: hay una API respondiendo en el puerto ${API_PORT:-8081}; detengala con Ctrl+C en su terminal."
fi

if [ "${1:-}" = "--all" ]; then
  if [ -n "${CATALINA_HOME:-}" ] && [ -d "$CATALINA_HOME/bin" ]; then
    echo "== Deteniendo Tomcat y retirando web1/web2 =="
    case "$(uname -s)" in
      MINGW*|MSYS*|CYGWIN*) cmd //c "$(cygpath -w "$CATALINA_HOME/bin/shutdown.bat")" >/dev/null 2>&1 ;;
      *) "$CATALINA_HOME/bin/shutdown.sh" >/dev/null 2>&1 ;;
    esac
    sleep 3
    rm -rf "$CATALINA_HOME/webapps/web1" "$CATALINA_HOME/webapps/web1.war" "$CATALINA_HOME/webapps/web2" "$CATALINA_HOME/webapps/web2.war"
  fi
  echo "== Eliminando contenedor y volumen de PostgreSQL =="
  docker compose -f docker/docker-compose.yml down -v
fi
echo "Limpieza terminada."
