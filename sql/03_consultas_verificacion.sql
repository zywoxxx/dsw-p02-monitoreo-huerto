-- ============================================================
--  03_consultas_verificacion.sql : evidencia de persistencia (PR09 / P02)
--  Ejecutar: psql -U huerto_app -d huerto_db -f sql/03_consultas_verificacion.sql
-- ============================================================

-- a) Version del servidor y base activa
SELECT version();
SELECT current_database() AS base, current_user AS usuario;

-- b) Tablas del modelo (deben ser 7)
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- c) Conteo por entidad
SELECT 'zona' AS entidad, count(*) AS registros FROM zona
UNION ALL SELECT 'variable',  count(*) FROM variable
UNION ALL SELECT 'sensor',    count(*) FROM sensor
UNION ALL SELECT 'umbral',    count(*) FROM umbral
UNION ALL SELECT 'lectura',   count(*) FROM lectura
UNION ALL SELECT 'alerta',    count(*) FROM alerta
UNION ALL SELECT 'anotacion', count(*) FROM anotacion;

-- d) Ultimas lecturas con sensor, variable, zona, procedencia y alerta (si existe)
SELECT l.id, s.codigo, v.nombre AS variable, z.nombre AS zona,
       l.valor, v.unidad, l.origen, l.observacion, l.registrado_en,
       a.nivel AS alerta
FROM lectura l
JOIN sensor s      ON s.id = l.sensor_id
JOIN variable v    ON v.id = s.variable_id
JOIN zona z        ON z.id = s.zona_id
LEFT JOIN alerta a ON a.lectura_id = l.id
ORDER BY l.registrado_en DESC
LIMIT 10;

-- e) Alertas generadas
SELECT a.id, s.codigo, a.nivel, a.mensaje, a.atendida, a.creada_en
FROM alerta a
JOIN lectura l ON l.id = a.lectura_id
JOIN sensor s  ON s.id = l.sensor_id
ORDER BY a.creada_en DESC;

-- f) Anotaciones recientes por zona y rol
SELECT n.id, z.nombre AS zona, n.autor_rol, n.texto, n.lectura_id, n.creada_en
FROM anotacion n
JOIN zona z ON z.id = n.zona_id
ORDER BY n.creada_en DESC
LIMIT 10;
