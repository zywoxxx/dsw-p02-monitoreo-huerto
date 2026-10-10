package mx.uv.dsw.huerto.api.lecturas;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

import mx.uv.dsw.huerto.api.error.ApiError;
import mx.uv.dsw.huerto.api.sensores.Sensor;

/**
 * Reglas del huerto para una lectura, las mismas de P02/P03 (LecturaValidator) expresadas sobre el
 * cuerpo JSON. Clase pura, sin Spring ni JDBC, para probarla con JUnit.
 */
public final class ReglasLectura {

    public static final int DECIMALES_MAX = 2;
    public static final int OBSERVACION_MAX = 200;

    private ReglasLectura() {
    }

    /** Errores de forma de la peticion (HTTP 400). Lista vacia si todo esta bien. */
    public static List<ApiError.Campo> validarForma(LecturaRequest r) {
        List<ApiError.Campo> errores = new ArrayList<>();
        if (r.getSensorId() == null) {
            errores.add(new ApiError.Campo("sensorId", "Debe indicar el sensor."));
        } else if (r.getSensorId() <= 0) {
            errores.add(new ApiError.Campo("sensorId", "El identificador del sensor no es valido."));
        }
        if (r.getValor() == null) {
            errores.add(new ApiError.Campo("valor", "El valor de la lectura es obligatorio."));
        } else if (r.getValor().scale() > DECIMALES_MAX) {
            errores.add(new ApiError.Campo("valor", "El valor admite como maximo " + DECIMALES_MAX
                + " decimales; no se redondea."));
        }
        if (r.getObservacion() != null && r.getObservacion().trim().length() > OBSERVACION_MAX) {
            errores.add(new ApiError.Campo("observacion", "La observacion no puede exceder " + OBSERVACION_MAX + " caracteres."));
        }
        return errores;
    }

    /** true si el valor esta dentro del rango fisico de la variable (limites incluidos). */
    public static boolean dentroDelRangoFisico(Sensor s, BigDecimal valor) {
        return valor.compareTo(s.getRangoFisicoMinimo()) >= 0 && valor.compareTo(s.getRangoFisicoMaximo()) <= 0;
    }

    /** "BAJA", "ALTA" o null si el valor esta dentro del umbral (limites incluidos) o no hay umbral. */
    public static String nivelAlerta(Sensor s, BigDecimal valor) {
        if (s.getUmbralMinimo() == null || s.getUmbralMaximo() == null) {
            return null;
        }
        if (valor.compareTo(s.getUmbralMinimo()) < 0) {
            return "BAJA";
        }
        if (valor.compareTo(s.getUmbralMaximo()) > 0) {
            return "ALTA";
        }
        return null;
    }

    public static String mensajeAlerta(Sensor s, BigDecimal valor, String nivel) {
        String limite = "BAJA".equals(nivel)
            ? "por debajo del minimo " + s.getUmbralMinimo().toPlainString()
            : "por encima del maximo " + s.getUmbralMaximo().toPlainString();
        return s.getVariable() + " en " + s.getZona() + ": " + valor.toPlainString() + " " + s.getUnidad()
            + " " + limite + " " + s.getUnidad() + ".";
    }
}
