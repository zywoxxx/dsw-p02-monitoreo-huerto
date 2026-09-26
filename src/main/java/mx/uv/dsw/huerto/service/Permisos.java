package mx.uv.dsw.huerto.service;

import java.util.Collections;
import java.util.EnumSet;
import java.util.Map;
import java.util.Set;

/**
 * Permisos por rol funcional, derivados del acta del PR09 (seccion 2, "Roles funcionales del sistema"):
 * el observador captura lecturas y anotaciones; el responsable y coordinacion consultan y anotan.
 * Si el equipo decide que el responsable tambien capture lecturas, basta cambiar este mapa.
 */
public final class Permisos {

    public enum Permiso { CONSULTAR, REGISTRAR_LECTURA, ANOTAR }

    public static final String ROL_RESPONSABLE = "RESPONSABLE";
    public static final String ROL_OBSERVADOR = "OBSERVADOR";
    public static final String ROL_COORDINACION = "COORDINACION";

    private static final Map<String, Set<Permiso>> POR_ROL = Map.of(
        ROL_OBSERVADOR, EnumSet.of(Permiso.CONSULTAR, Permiso.REGISTRAR_LECTURA, Permiso.ANOTAR),
        ROL_RESPONSABLE, EnumSet.of(Permiso.CONSULTAR, Permiso.ANOTAR),
        ROL_COORDINACION, EnumSet.of(Permiso.CONSULTAR, Permiso.ANOTAR)
    );

    private Permisos() {
    }

    public static boolean tiene(String rol, Permiso permiso) {
        return rol != null && POR_ROL.getOrDefault(rol, Collections.emptySet()).contains(permiso);
    }

    public static boolean esRolValido(String rol) {
        return rol != null && POR_ROL.containsKey(rol);
    }
}
