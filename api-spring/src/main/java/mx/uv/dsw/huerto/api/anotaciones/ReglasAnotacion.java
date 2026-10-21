package mx.uv.dsw.huerto.api.anotaciones;

import java.util.ArrayList;
import java.util.List;

import mx.uv.dsw.huerto.api.error.ApiError;

/**
 * Reglas de forma de una anotacion, las mismas que ck_anotacion_texto y el largo de la columna
 * expresadas sobre el cuerpo JSON. Clase pura, sin Spring ni JDBC, para probarla con JUnit.
 */
public final class ReglasAnotacion {

    public static final int TEXTO_MIN = 3;
    public static final int TEXTO_MAX = 300;

    private ReglasAnotacion() {
    }

    /** Errores de forma de la peticion (HTTP 400). El texto se recorta antes de medirlo. Lista vacia si todo esta bien. */
    public static List<ApiError.Campo> validarForma(AnotacionRequest r) {
        List<ApiError.Campo> errores = new ArrayList<>();
        if (r.getZonaId() == null) {
            errores.add(new ApiError.Campo("zonaId", "Debe indicar la zona."));
        } else if (r.getZonaId() <= 0) {
            errores.add(new ApiError.Campo("zonaId", "El identificador de la zona no es valido."));
        }
        if (r.getLecturaId() != null && r.getLecturaId() <= 0) {
            errores.add(new ApiError.Campo("lecturaId", "El identificador de la lectura no es valido."));
        }
        if (r.getTexto() == null) {
            errores.add(new ApiError.Campo("texto", "El texto de la anotacion es obligatorio."));
        } else if (r.getTexto().trim().length() < TEXTO_MIN) {
            errores.add(new ApiError.Campo("texto", "La anotacion debe tener al menos " + TEXTO_MIN + " caracteres."));
        } else if (r.getTexto().trim().length() > TEXTO_MAX) {
            errores.add(new ApiError.Campo("texto", "La anotacion no puede exceder " + TEXTO_MAX + " caracteres."));
        }
        return errores;
    }
}
