-- ============================================================
--  04_p05_atencion_alerta.sql : migracion no destructiva del incremento P05 (PR09)
--  Agrega a alerta el instante y el rol que la atendio (PATCH /api/alertas/{id}).
--  Idempotente: se puede ejecutar varias veces sobre una base ya migrada.
--  Ejecutar: psql -U huerto_app -d huerto_db -v ON_ERROR_STOP=1 -f sql/04_p05_atencion_alerta.sql
-- ============================================================

BEGIN;

ALTER TABLE alerta ADD COLUMN IF NOT EXISTS atendida_en  TIMESTAMPTZ;
ALTER TABLE alerta ADD COLUMN IF NOT EXISTS atendida_por VARCHAR(15);

-- Una alerta atendida lleva instante y rol; una pendiente no lleva ninguno de los dos
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_alerta_atencion' AND conrelid = 'alerta'::regclass
    ) THEN
        ALTER TABLE alerta ADD CONSTRAINT ck_alerta_atencion CHECK (
            (atendida AND atendida_en IS NOT NULL
                AND atendida_por IN ('RESPONSABLE', 'OBSERVADOR', 'COORDINACION'))
            OR (NOT atendida AND atendida_en IS NULL AND atendida_por IS NULL)
        );
    END IF;
END $$;

COMMENT ON COLUMN alerta.atendida_en  IS 'Instante en que se atendio la alerta; NULL mientras esta pendiente';
COMMENT ON COLUMN alerta.atendida_por IS 'Rol funcional que la atendio; NULL mientras esta pendiente';

COMMIT;
