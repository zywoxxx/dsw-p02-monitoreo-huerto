package mx.uv.dsw.huerto.api.seguridad;

import javax.servlet.http.HttpServletRequest;

import mx.uv.dsw.huerto.api.error.ApiException;
import mx.uv.dsw.huerto.api.seguridad.Permisos.Permiso;

/** Identidad que el filtro extrae del token y deja en la peticion. La API no guarda sesion. */
public class UsuarioAutenticado {

    static final String ATRIBUTO = "huerto.usuario";

    private final String nombre;
    private final String rol;

    public UsuarioAutenticado(String nombre, String rol) {
        this.nombre = nombre;
        this.rol = rol;
    }

    public String getNombre() {
        return nombre;
    }

    public String getRol() {
        return rol;
    }

    /** Usuario de la peticion actual; 401 si el filtro no lo dejo (no deberia ocurrir en rutas protegidas). */
    public static UsuarioAutenticado de(HttpServletRequest request) {
        Object u = request.getAttribute(ATRIBUTO);
        if (!(u instanceof UsuarioAutenticado)) {
            throw ApiException.noAutenticado("Se requiere un token valido.");
        }
        return (UsuarioAutenticado) u;
    }

    /** Comprueba el permiso en el servidor; 403 si el rol no lo tiene. */
    public void exigir(Permiso permiso) {
        if (!Permisos.tiene(rol, permiso)) {
            throw ApiException.prohibido("El rol " + rol + " no tiene permiso para esta operacion.");
        }
    }
}
