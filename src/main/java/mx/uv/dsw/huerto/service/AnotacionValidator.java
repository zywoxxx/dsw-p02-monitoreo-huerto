package mx.uv.dsw.huerto.service;

import java.util.Arrays;
import java.util.List;

/**
 * Reglas de validacion de una anotacion (RF06). Clase pura, sin JDBC ni HTTP, probada con JUnit.
 * Los roles funcionales del PR09 son exactamente tres: RESPONSABLE, OBSERVADOR y COORDINACION.
 */
public final class AnotacionValidator {

    public static final List<String> ROLES = Arrays.asList("RESPONSABLE", "OBSERVADOR", "COORDINACION");
    public static final int TEXTO_MIN = 3;
    public static final int TEXTO_MAX = 300;

    private AnotacionValidator() {
    }

    /** Valida el id de zona; devuelve el id o null si es invalido. */
    public static Long parseZonaId(String zonaIdParam, List<String> errores) {
        if (zonaIdParam == null || zonaIdParam.isBlank()) {
            errores.add("Debe seleccionar una zona.");
            return null;
        }
        try {
            long id = Long.parseLong(zonaIdParam.trim());
            if (id <= 0) {
                errores.add("El identificador de la zona no es valido.");
                return null;
            }
            return id;
        } catch (NumberFormatException e) {
            errores.add("El identificador de la zona no es valido.");
            return null;
        }
    }

    /** Valida el id de lectura opcional; devuelve null si viene vacio. */
    public static Long parseLecturaId(String lecturaIdParam, List<String> errores) {
        if (lecturaIdParam == null || lecturaIdParam.isBlank()) {
            return null;
        }
        try {
            long id = Long.parseLong(lecturaIdParam.trim());
            if (id <= 0) {
                errores.add("El identificador de la lectura no es valido.");
                return null;
            }
            return id;
        } catch (NumberFormatException e) {
            errores.add("El identificador de la lectura no es valido.");
            return null;
        }
    }

    /** Valida que el rol sea uno de los tres roles funcionales. */
    public static String parseRol(String rolParam, List<String> errores) {
        if (rolParam == null || rolParam.isBlank()) {
            errores.add("Debe indicar el rol que anota (RESPONSABLE, OBSERVADOR o COORDINACION).");
            return null;
        }
        String rol = rolParam.trim().toUpperCase();
        if (!ROLES.contains(rol)) {
            errores.add("El rol '" + rolParam.trim() + "' no es valido; use RESPONSABLE, OBSERVADOR o COORDINACION.");
            return null;
        }
        return rol;
    }

    /** Valida el texto: obligatorio, entre 3 y 300 caracteres. */
    public static String parseTexto(String textoParam, List<String> errores) {
        if (textoParam == null || textoParam.trim().length() < TEXTO_MIN) {
            errores.add("La anotacion debe tener al menos " + TEXTO_MIN + " caracteres.");
            return null;
        }
        String texto = textoParam.trim();
        if (texto.length() > TEXTO_MAX) {
            errores.add("La anotacion no puede exceder " + TEXTO_MAX + " caracteres.");
            return null;
        }
        return texto;
    }
}
