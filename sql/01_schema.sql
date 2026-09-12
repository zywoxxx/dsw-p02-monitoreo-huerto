-- ============================================================
--  PR09 Monitoreo de huerto o ambiente - Incremento P02
--  01_schema.sql : modelo de datos (7 entidades), PostgreSQL 16
--  Entidades de la ficha C11/PR09: zona, variable, lectura, umbral,
--  alerta, anotacion. Extension justificada: sensor (dispositivo que
--  mide una variable en una zona; sera la fuente IoT simulada en Web 4.0).
--  Ejecutar: psql -U huerto_app -d huerto_db -f sql/01_schema.sql
-- ============================================================

BEGIN;

-- 1. ZONA (RF01): cama, invernadero o parcela del huerto que se monitorea
CREATE TABLE IF NOT EXISTS zona (
    id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre    VARCHAR(80)  NOT NULL UNIQUE,
    cultivo   VARCHAR(80),
    ubicacion VARCHAR(120) NOT NULL,
    creada_en TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE zona IS 'Zona o cama de cultivo del huerto (datos ficticios)';

-- 2. VARIABLE (RF02): magnitud ambiental medible y su rango fisico valido
CREATE TABLE IF NOT EXISTS variable (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave         VARCHAR(30) NOT NULL UNIQUE,
    nombre        VARCHAR(60) NOT NULL,
    unidad        VARCHAR(10) NOT NULL,
    valor_minimo  NUMERIC(10,2) NOT NULL,
    valor_maximo  NUMERIC(10,2) NOT NULL,
    CONSTRAINT ck_variable_rango CHECK (valor_minimo < valor_maximo)
);
COMMENT ON TABLE variable IS 'Variable ambiental (temperatura, humedad, luz) con unidad y rango fisico aceptable';

-- 3. SENSOR (extension): dispositivo, fisico o simulado, que mide una variable en una zona
CREATE TABLE IF NOT EXISTS sensor (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    zona_id      BIGINT      NOT NULL REFERENCES zona(id) ON DELETE CASCADE,
    variable_id  BIGINT      NOT NULL REFERENCES variable(id),
    codigo       VARCHAR(20) NOT NULL UNIQUE,
    activo       BOOLEAN     NOT NULL DEFAULT TRUE,
    instalado_en DATE        NOT NULL DEFAULT CURRENT_DATE
);
COMMENT ON TABLE sensor IS 'Dispositivo que mide una variable en una zona; en Web 4.0 sera la fuente simulada';

-- 4. UMBRAL (RF04): rango operativo deseado por sensor; fuera de el se genera alerta
CREATE TABLE IF NOT EXISTS umbral (
    id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id BIGINT        NOT NULL UNIQUE REFERENCES sensor(id) ON DELETE CASCADE,
    minimo    NUMERIC(10,2) NOT NULL,
    maximo    NUMERIC(10,2) NOT NULL,
    CONSTRAINT ck_umbral_rango CHECK (minimo < maximo)
);
COMMENT ON TABLE umbral IS 'Rango operativo del sensor; una lectura fuera del rango genera alerta';

-- 5. LECTURA (RF03, RF05): medicion con instante, valor y procedencia (manual o simulado)
CREATE TABLE IF NOT EXISTS lectura (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id     BIGINT        NOT NULL REFERENCES sensor(id) ON DELETE CASCADE,
    valor         NUMERIC(10,2) NOT NULL,
    origen        VARCHAR(10)   NOT NULL DEFAULT 'manual',
    observacion   VARCHAR(200),
    registrado_en TIMESTAMPTZ   NOT NULL DEFAULT now(),
    CONSTRAINT ck_lectura_origen CHECK (origen IN ('manual', 'simulado'))
);
COMMENT ON TABLE lectura IS 'Medicion registrada; origen etiqueta si es captura manual o simulacion (riesgo PR09)';
CREATE INDEX IF NOT EXISTS idx_lectura_sensor_fecha ON lectura (sensor_id, registrado_en DESC);

-- 6. ALERTA (RF06): aviso generado cuando una lectura sale del umbral
CREATE TABLE IF NOT EXISTS alerta (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lectura_id BIGINT       NOT NULL UNIQUE REFERENCES lectura(id) ON DELETE CASCADE,
    nivel      VARCHAR(10)  NOT NULL,
    mensaje    VARCHAR(200) NOT NULL,
    atendida   BOOLEAN      NOT NULL DEFAULT FALSE,
    creada_en  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT ck_alerta_nivel CHECK (nivel IN ('BAJA', 'ALTA'))
);
COMMENT ON TABLE alerta IS 'Alerta generada automaticamente por una lectura fuera del umbral';

-- 7. ANOTACION (RF06): nota de un rol funcional sobre una zona (y opcionalmente sobre una lectura)
CREATE TABLE IF NOT EXISTS anotacion (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    zona_id    BIGINT       NOT NULL REFERENCES zona(id) ON DELETE CASCADE,
    lectura_id BIGINT       REFERENCES lectura(id) ON DELETE SET NULL,
    autor_rol  VARCHAR(15)  NOT NULL,
    texto      VARCHAR(300) NOT NULL,
    creada_en  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT ck_anotacion_rol CHECK (autor_rol IN ('RESPONSABLE', 'OBSERVADOR', 'COORDINACION')),
    CONSTRAINT ck_anotacion_texto CHECK (length(trim(texto)) >= 3)
);
COMMENT ON TABLE anotacion IS 'Anotacion de un rol funcional (responsable, observador, coordinacion) sobre una zona';
CREATE INDEX IF NOT EXISTS idx_anotacion_zona_fecha ON anotacion (zona_id, creada_en DESC);

COMMIT;
