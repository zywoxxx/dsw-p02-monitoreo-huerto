-- ============================================================
--  99_cleanup.sql : borra SOLO las lecturas y alertas creadas durante
--  las pruebas HTTP (origen = 'manual'). Conserva catalogo y semilla.
-- ============================================================
BEGIN;
DELETE FROM alerta  WHERE lectura_id IN (SELECT id FROM lectura WHERE origen = 'manual');
DELETE FROM lectura WHERE origen = 'manual';
COMMIT;

SELECT 'lecturas restantes' AS dato, count(*) AS total FROM lectura
UNION ALL SELECT 'alertas restantes', count(*) FROM alerta;
