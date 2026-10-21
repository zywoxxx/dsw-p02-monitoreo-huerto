package mx.uv.dsw.huerto.api.seguridad;

import java.util.Collections;
import java.util.EnumSet;
import java.util.Map;
import java.util.Set;

/**
 * Permisos por rol funcional del PR09 (acta, seccion 2): el observador captura lecturas y anota; el
 * responsable y coordinacion consultan y anotan. Desde P05 solo el responsable atiende o reabre
 * alertas, porque en el acta es quien "anota decisiones" sobre el huerto. Son exactamente tres roles.
 */
public final class Permisos {

    public enum Permiso { CONSULTAR, REGISTRAR_LECTURA, ANOTAR, ATENDER_ALERTA }

    private static final Map<String, Set<Permiso>> POR_ROL = Map.of(
        "OBSERVADOR", EnumSet.of(Permiso.CONSULTAR, Permiso.REGISTRAR_LECTURA, Permiso.ANOTAR),
        "RESPONSABLE", EnumSet.of(Permiso.CONSULTAR, Permiso.ANOTAR, Permiso.ATENDER_ALERTA),
        "COORDINACION", EnumSet.of(Permiso.CONSULTAR, Permiso.ANOTAR)
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
