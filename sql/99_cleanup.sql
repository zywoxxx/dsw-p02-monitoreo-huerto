-- ============================================================
--  99_cleanup.sql : borra SOLO los datos creados durante las pruebas HTTP:
--  lecturas con origen = 'manual' (y sus alertas) y anotaciones cuyo texto
--  empieza con '[prueba]'. Conserva catalogo y semilla.
-- ============================================================
BEGIN;
DELETE FROM alerta    WHERE lectura_id IN (SELECT id FROM lectura WHERE origen = 'manual');
DELETE FROM anotacion WHERE texto LIKE '[prueba]%' OR lectura_id IN (SELECT id FROM lectura WHERE origen = 'manual');
DELETE FROM lectura   WHERE origen = 'manual';
COMMIT;

SELECT 'lecturas restantes' AS dato, count(*) AS total FROM lectura
UNION ALL SELECT 'alertas restantes',     count(*) FROM alerta
UNION ALL SELECT 'anotaciones restantes', count(*) FROM anotacion;
