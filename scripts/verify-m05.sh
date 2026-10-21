#!/usr/bin/env bash
# ============================================================================
#  verify-m05.sh  -  Verificacion reproducible de P05 (integracion Angular - Spring Boot - PostgreSQL)
#
#  Lo invoca  ./scripts/verify-module.sh M05
#  Es un envoltorio de scripts/verify-m04.sh: mismos pasos con etiqueta [M05], evidencia en
#  docs/p05/evidencia/{txt,img} y, antes de arrancar la API, la migracion idempotente
#  sql/04_p05_atencion_alerta.sql (columnas atendida_en y atendida_por de alerta), cuya salida
#  queda en 08b_migracion_p05.txt. Acepta las mismas variables que verify-m04.sh
#  (API_PORT, PSQL_CMD, CHROME_BIN, SKIP_FRONT, SKIP_NAVEGADOR, WEB_PORT, DB_*).
# ============================================================================
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODULO=M05 EVID="$ROOT/docs/p05/evidencia/txt" IMG="$ROOT/docs/p05/evidencia/img" exec bash "$ROOT/scripts/verify-m04.sh"
