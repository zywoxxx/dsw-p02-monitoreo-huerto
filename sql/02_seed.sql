-- ============================================================
--  02_seed.sql : datos de prueba FICTICIOS para el incremento P02
--  Ejecutar despues de 01_schema.sql
-- ============================================================
BEGIN;

INSERT INTO huerto (nombre, ubicacion, descripcion) VALUES
  ('Huerto escolar demo', 'Patio norte (ficticio)', 'Huerto de practicas para el laboratorio DSW')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO zona (huerto_id, nombre, cultivo)
SELECT h.id, z.nombre, z.cultivo
FROM huerto h
JOIN (VALUES ('Cama A', 'Jitomate'), ('Invernadero 1', 'Lechuga')) AS z(nombre, cultivo) ON TRUE
WHERE h.nombre = 'Huerto escolar demo'
ON CONFLICT (huerto_id, nombre) DO NOTHING;

INSERT INTO tipo_sensor (clave, nombre, unidad, valor_minimo, valor_maximo) VALUES
  ('TEMP',    'Temperatura ambiente', 'C',   -10.00, 60.00),
  ('HUM_SUE', 'Humedad de suelo',     '%',     0.00, 100.00),
  ('HUM_AIR', 'Humedad relativa',     '%',     0.00, 100.00),
  ('LUZ',     'Luminosidad',          'lux',   0.00, 100000.00)
ON CONFLICT (clave) DO NOTHING;

INSERT INTO sensor (zona_id, tipo_sensor_id, codigo)
SELECT z.id, t.id, s.codigo
FROM (VALUES
  ('Cama A',        'TEMP',    'SEN-A-TEMP-01'),
  ('Cama A',        'HUM_SUE', 'SEN-A-HSUE-01'),
  ('Invernadero 1', 'TEMP',    'SEN-I1-TEMP-01'),
  ('Invernadero 1', 'HUM_AIR', 'SEN-I1-HAIR-01'),
  ('Invernadero 1', 'LUZ',     'SEN-I1-LUZ-01')
) AS s(zona, tipo, codigo)
JOIN zona z        ON z.nombre = s.zona
JOIN tipo_sensor t ON t.clave  = s.tipo
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO umbral (sensor_id, minimo, maximo)
SELECT s.id, u.minimo, u.maximo
FROM (VALUES
  ('SEN-A-TEMP-01',    15.00,    32.00),
  ('SEN-A-HSUE-01',    40.00,    80.00),
  ('SEN-I1-TEMP-01',   18.00,    30.00),
  ('SEN-I1-HAIR-01',   50.00,    85.00),
  ('SEN-I1-LUZ-01',  2000.00, 60000.00)
) AS u(codigo, minimo, maximo)
JOIN sensor s ON s.codigo = u.codigo
ON CONFLICT (sensor_id) DO NOTHING;

-- Dos lecturas iniciales dentro de rango (sin alerta) para que el GET inicial no este vacio
INSERT INTO lectura (sensor_id, valor, origen, observacion)
SELECT s.id, l.valor, 'simulado', l.obs
FROM (VALUES
  ('SEN-A-TEMP-01', 24.50, 'Carga inicial del laboratorio'),
  ('SEN-A-HSUE-01', 55.00, 'Carga inicial del laboratorio')
) AS l(codigo, valor, obs)
JOIN sensor s ON s.codigo = l.codigo
WHERE NOT EXISTS (SELECT 1 FROM lectura);

COMMIT;
