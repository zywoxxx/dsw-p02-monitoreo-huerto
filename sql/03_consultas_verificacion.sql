-- ============================================================
--  03_consultas_verificacion.sql : evidencia de persistencia
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
SELECT 'huerto' AS entidad, count(*) AS registros FROM huerto
UNION ALL SELECT 'zona',        count(*) FROM zona
UNION ALL SELECT 'tipo_sensor', count(*) FROM tipo_sensor
UNION ALL SELECT 'sensor',      count(*) FROM sensor
UNION ALL SELECT 'umbral',      count(*) FROM umbral
UNION ALL SELECT 'lectura',     count(*) FROM lectura
UNION ALL SELECT 'alerta',      count(*) FROM alerta;

-- d) Ultimas lecturas con su sensor, zona, huerto y alerta (si existe)
SELECT l.id, s.codigo, z.nombre AS zona, h.nombre AS huerto,
       l.valor, t.unidad, l.origen, l.observacion, l.registrado_en,
       a.nivel AS alerta
FROM lectura l
JOIN sensor s      ON s.id = l.sensor_id
JOIN tipo_sensor t ON t.id = s.tipo_sensor_id
JOIN zona z        ON z.id = s.zona_id
JOIN huerto h      ON h.id = z.huerto_id
LEFT JOIN alerta a ON a.lectura_id = l.id
ORDER BY l.registrado_en DESC
LIMIT 10;

-- e) Alertas generadas
SELECT a.id, s.codigo, a.nivel, a.mensaje, a.atendida, a.creada_en
FROM alerta a
JOIN lectura l ON l.id = a.lectura_id
JOIN sensor s  ON s.id = l.sensor_id
ORDER BY a.creada_en DESC;
