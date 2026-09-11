package mx.uv.dsw.huerto.service;

import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;

import mx.uv.dsw.huerto.config.DbConfig;
import mx.uv.dsw.huerto.model.Sensor;
import mx.uv.dsw.huerto.repository.LecturaRepository;
import mx.uv.dsw.huerto.repository.SensorRepository;

/**
 * Caso de uso "Registrar lectura" (flujo principal del PRxx en P02).
 * Coordina validacion (RF-03), persistencia (RF-02) y generacion de alerta (RF-05)
 * en una sola transaccion JDBC: si falla la alerta, tampoco queda la lectura.
 */
public class LecturaService {

    /** Resultado del registro: id de la lectura creada y nivel de alerta (o null). */
    public static final class Resultado {
        private final long lecturaId;
        private final String alertaNivel;

        Resultado(long lecturaId, String alertaNivel) {
            this.lecturaId = lecturaId;
            this.alertaNivel = alertaNivel;
        }

        public long getLecturaId() {
            return lecturaId;
        }

        public String getAlertaNivel() {
            return alertaNivel;
        }
    }

    private final SensorRepository sensorRepository;
    private final LecturaRepository lecturaRepository;

    public LecturaService() {
        this(new SensorRepository(), new LecturaRepository());
    }

    public LecturaService(SensorRepository sensorRepository, LecturaRepository lecturaRepository) {
        this.sensorRepository = sensorRepository;
        this.lecturaRepository = lecturaRepository;
    }

    /**
     * Valida los parametros crudos del formulario y persiste la lectura.
     *
     * @throws ValidacionException si la entrada es invalida (el servlet responde 400).
     * @throws SQLException        si PostgreSQL no esta disponible (el servlet responde 500/503).
     */
    public Resultado registrar(String sensorIdParam, String valorParam, String observacionParam)
            throws ValidacionException, SQLException {

        // 1) Validacion sintactica sin tocar la base de datos
        List<String> errores = LecturaValidator.nuevaListaErrores();
        Long sensorId = LecturaValidator.parseSensorId(sensorIdParam, errores);
        BigDecimal valor = LecturaValidator.parseValor(valorParam, errores);
        String observacion = LecturaValidator.parseObservacion(observacionParam, errores);
        if (!errores.isEmpty()) {
            throw new ValidacionException(errores);
        }

        // 2) Validacion semantica + persistencia en una transaccion
        try (Connection cn = DbConfig.getConnection()) {
            cn.setAutoCommit(false);
            try {
                Optional<Sensor> encontrado = sensorRepository.findById(cn, sensorId);
                if (encontrado.isEmpty()) {
                    errores.add("El sensor seleccionado no existe.");
                    throw new ValidacionException(errores);
                }
                Sensor sensor = encontrado.get();
                LecturaValidator.validarRangoFisico(sensor, valor, errores);
                if (!errores.isEmpty()) {
                    throw new ValidacionException(errores);
                }

                long lecturaId = lecturaRepository.insertLectura(cn, sensor.getId(), valor, observacion);
                String nivel = LecturaValidator.nivelAlerta(sensor, valor);
                if (nivel != null) {
                    lecturaRepository.insertAlerta(cn, lecturaId, nivel,
                        LecturaValidator.mensajeAlerta(sensor, valor, nivel));
                }
                cn.commit();
                return new Resultado(lecturaId, nivel);
            } catch (ValidacionException | SQLException | RuntimeException e) {
                cn.rollback();
                throw e;
            } finally {
                cn.setAutoCommit(true);
            }
        }
    }
}
