#!/usr/bin/env bash
# ============================================================================
#  cleanup.sh  -  Limpieza de recursos locales del incremento P02
#
#  Sin argumentos : borra SOLO las lecturas/alertas creadas por las pruebas
#                   (origen = 'manual') y la carpeta target/. Conserva semilla.
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

echo "== Eliminando target/ =="
rm -rf target

if [ "${1:-}" = "--all" ]; then
  if [ -n "${CATALINA_HOME:-}" ] && [ -d "$CATALINA_HOME/bin" ]; then
    echo "== Deteniendo Tomcat y retirando web1 =="
    case "$(uname -s)" in
      MINGW*|MSYS*|CYGWIN*) cmd //c "$(cygpath -w "$CATALINA_HOME/bin/shutdown.bat")" >/dev/null 2>&1 ;;
      *) "$CATALINA_HOME/bin/shutdown.sh" >/dev/null 2>&1 ;;
    esac
    sleep 3
    rm -rf "$CATALINA_HOME/webapps/web1" "$CATALINA_HOME/webapps/web1.war"
  fi
  echo "== Eliminando contenedor y volumen de PostgreSQL =="
  docker compose -f docker/docker-compose.yml down -v
fi
echo "Limpieza terminada."
