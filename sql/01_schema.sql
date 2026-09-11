-- ============================================================
--  PRxx Monitoreo de huerto - Incremento P02
--  01_schema.sql : modelo de datos (7 entidades), PostgreSQL 16
--  Ejecutar: psql -U huerto_app -d huerto_db -f sql/01_schema.sql
-- ============================================================

BEGIN;

-- 1. HUERTO: sitio fisico que se monitorea
CREATE TABLE IF NOT EXISTS huerto (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      VARCHAR(80)  NOT NULL UNIQUE,
    ubicacion   VARCHAR(120) NOT NULL,
    descripcion TEXT,
    creado_en   TIMESTAMPTZ  NOT NULL DEFAULT now()
);
COMMENT ON TABLE huerto IS 'Huerto o ambiente controlado que se monitorea';

-- 2. ZONA: subdivision del huerto (cama, invernadero, parcela)
CREATE TABLE IF NOT EXISTS zona (
    id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    huerto_id BIGINT      NOT NULL REFERENCES huerto(id) ON DELETE CASCADE,
    nombre    VARCHAR(80) NOT NULL,
    cultivo   VARCHAR(80),
    UNIQUE (huerto_id, nombre)
);
COMMENT ON TABLE zona IS 'Zona o cama de cultivo dentro de un huerto';

-- 3. TIPO_SENSOR: catalogo de magnitudes medibles y su rango fisico valido
CREATE TABLE IF NOT EXISTS tipo_sensor (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave         VARCHAR(30) NOT NULL UNIQUE,
    nombre        VARCHAR(60) NOT NULL,
    unidad        VARCHAR(10) NOT NULL,
    valor_minimo  NUMERIC(10,2) NOT NULL,
    valor_maximo  NUMERIC(10,2) NOT NULL,
    CONSTRAINT ck_tipo_sensor_rango CHECK (valor_minimo < valor_maximo)
);
COMMENT ON TABLE tipo_sensor IS 'Magnitud que mide un sensor y el rango fisico aceptable de una lectura';

-- 4. SENSOR: dispositivo instalado en una zona
CREATE TABLE IF NOT EXISTS sensor (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    zona_id        BIGINT      NOT NULL REFERENCES zona(id) ON DELETE CASCADE,
    tipo_sensor_id BIGINT      NOT NULL REFERENCES tipo_sensor(id),
    codigo         VARCHAR(20) NOT NULL UNIQUE,
    activo         BOOLEAN     NOT NULL DEFAULT TRUE,
    instalado_en   DATE        NOT NULL DEFAULT CURRENT_DATE
);
COMMENT ON TABLE sensor IS 'Sensor fisico o simulado instalado en una zona';

-- 5. UMBRAL: rango operativo deseado para un sensor; fuera de el se genera alerta
CREATE TABLE IF NOT EXISTS umbral (
    id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id BIGINT        NOT NULL UNIQUE REFERENCES sensor(id) ON DELETE CASCADE,
    minimo    NUMERIC(10,2) NOT NULL,
    maximo    NUMERIC(10,2) NOT NULL,
    CONSTRAINT ck_umbral_rango CHECK (minimo < maximo)
);
COMMENT ON TABLE umbral IS 'Rango operativo del sensor; una lectura fuera del rango genera alerta';

-- 6. LECTURA: medicion registrada (flujo principal del incremento)
CREATE TABLE IF NOT EXISTS lectura (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id     BIGINT        NOT NULL REFERENCES sensor(id) ON DELETE CASCADE,
    valor         NUMERIC(10,2) NOT NULL,
    origen        VARCHAR(10)   NOT NULL DEFAULT 'manual',
    observacion   VARCHAR(200),
    registrado_en TIMESTAMPTZ   NOT NULL DEFAULT now(),
    CONSTRAINT ck_lectura_origen CHECK (origen IN ('manual', 'simulado'))
);
COMMENT ON TABLE lectura IS 'Medicion de un sensor registrada por el operador o por un simulador';
CREATE INDEX IF NOT EXISTS idx_lectura_sensor_fecha ON lectura (sensor_id, registrado_en DESC);

-- 7. ALERTA: aviso generado cuando una lectura sale del umbral
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

COMMIT;
