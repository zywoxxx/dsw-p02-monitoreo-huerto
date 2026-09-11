package mx.uv.dsw.huerto.service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

import mx.uv.dsw.huerto.model.Sensor;

/**
 * Reglas de validacion de una lectura (RF-03). Es una clase pura, sin JDBC ni HTTP,
 * para que pueda probarse con JUnit sin levantar Tomcat ni PostgreSQL.
 *
 * <p>Entrada esperada: parametros crudos del formulario. Salida: valor numerico validado
 * o una {@link ValidacionException} con la lista de errores a mostrar en la JSP.
 */
public final class LecturaValidator {

    public static final int OBSERVACION_MAX = 200;
    public static final int DECIMALES_MAX = 2;

    private LecturaValidator() {
    }

    /** Valida el id de sensor recibido como texto; devuelve el id numerico o null si es invalido. */
    public static Long parseSensorId(String sensorIdParam, List<String> errores) {
        if (sensorIdParam == null || sensorIdParam.isBlank()) {
            errores.add("Debe seleccionar un sensor.");
            return null;
        }
        try {
            long id = Long.parseLong(sensorIdParam.trim());
            if (id <= 0) {
                errores.add("El identificador del sensor no es valido.");
                return null;
            }
            return id;
        } catch (NumberFormatException e) {
            errores.add("El identificador del sensor no es valido.");
            return null;
        }
    }

    /** Valida el valor: obligatorio, numerico, maximo 2 decimales. */
    public static BigDecimal parseValor(String valorParam, List<String> errores) {
        if (valorParam == null || valorParam.isBlank()) {
            errores.add("El valor de la lectura es obligatorio.");
            return null;
        }
        BigDecimal valor;
        try {
            valor = new BigDecimal(valorParam.trim().replace(',', '.'));
        } catch (NumberFormatException e) {
            errores.add("El valor debe ser numerico (ejemplo: 24.5).");
            return null;
        }
        if (valor.scale() > DECIMALES_MAX) {
            errores.add("El valor admite como maximo " + DECIMALES_MAX + " decimales.");
            return null;
        }
        return valor;
    }

    /** Valida la observacion opcional (longitud maxima). Devuelve el texto recortado o null. */
    public static String parseObservacion(String observacionParam, List<String> errores) {
        if (observacionParam == null || observacionParam.isBlank()) {
            return null;
        }
        String obs = observacionParam.trim();
        if (obs.length() > OBSERVACION_MAX) {
            errores.add("La observacion no puede exceder " + OBSERVACION_MAX + " caracteres.");
            return null;
        }
        return obs;
    }

    /** Valida que el valor este dentro del rango fisico del tipo de sensor. */
    public static void validarRangoFisico(Sensor sensor, BigDecimal valor, List<String> errores) {
        if (!sensor.isActivo()) {
            errores.add("El sensor " + sensor.getCodigo() + " esta inactivo; no admite lecturas.");
            return;
        }
        if (valor.compareTo(sensor.getValorMinimo()) < 0 || valor.compareTo(sensor.getValorMaximo()) > 0) {
            errores.add("El valor " + valor.toPlainString() + " " + sensor.getUnidad()
                + " esta fuera del rango fisico permitido para " + sensor.getTipoNombre()
                + " [" + sensor.getValorMinimo().toPlainString() + ", "
                + sensor.getValorMaximo().toPlainString() + "].");
        }
    }

    /**
     * RF-05: determina el nivel de alerta segun el umbral operativo del sensor.
     *
     * @return "BAJA" si el valor es menor al minimo, "ALTA" si es mayor al maximo, null si esta en rango
     *         o el sensor no tiene umbral.
     */
    public static String nivelAlerta(Sensor sensor, BigDecimal valor) {
        if (!sensor.isConUmbral()) {
            return null;
        }
        if (valor.compareTo(sensor.getUmbralMinimo()) < 0) {
            return "BAJA";
        }
        if (valor.compareTo(sensor.getUmbralMaximo()) > 0) {
            return "ALTA";
        }
        return null;
    }

    /** Mensaje legible de la alerta para persistir y mostrar. */
    public static String mensajeAlerta(Sensor sensor, BigDecimal valor, String nivel) {
        String limite = "BAJA".equals(nivel)
            ? "por debajo del minimo " + sensor.getUmbralMinimo().toPlainString()
            : "por encima del maximo " + sensor.getUmbralMaximo().toPlainString();
        return sensor.getTipoNombre() + " en " + sensor.getZona() + ": " + valor.toPlainString() + " "
            + sensor.getUnidad() + " " + limite + " " + sensor.getUnidad() + ".";
    }

    /** Lista mutable vacia para acumular errores; evita repetir new ArrayList en los llamadores. */
    public static List<String> nuevaListaErrores() {
        return new ArrayList<>();
    }
}
