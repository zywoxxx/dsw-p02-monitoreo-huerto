package mx.uv.dsw.huerto.web;

import java.io.Serializable;
import java.util.Optional;

import javax.enterprise.context.SessionScoped;
import javax.faces.context.ExternalContext;
import javax.faces.context.FacesContext;
import javax.inject.Inject;
import javax.inject.Named;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;

import mx.uv.dsw.huerto.model.Usuario;
import mx.uv.dsw.huerto.service.AuthService;
import mx.uv.dsw.huerto.service.Permisos;
import mx.uv.dsw.huerto.service.Permisos.Permiso;

/**
 * Identidad de la sesion: quien entro y con que rol. Es lo unico que se guarda en sesion;
 * el estado de los formularios vive en beans de vista.
 */
@Named("sesion")
@SessionScoped
public class SesionBean implements Serializable {

    private static final long serialVersionUID = 1L;

    /** Atributo plano de HttpSession que consulta AutenticacionFilter sin depender de CDI. */
    public static final String ATRIBUTO_USUARIO = "huerto.usuario";

    @Inject
    private AuthService authService;

    private Usuario usuario;
    private String nombreUsuario;
    private String contrasena;

    /** index.xhtml: manda al flujo principal o al acceso segun haya sesion. */
    public String inicio() {
        return isAutenticado() ? "/app/lecturas?faces-redirect=true" : "/login?faces-redirect=true";
    }

    public String iniciarSesion() {
        Optional<Usuario> encontrado = authService.autenticar(nombreUsuario, contrasena);
        contrasena = null;
        if (encontrado.isEmpty()) {
            Mensajes.error("No fue posible iniciar sesion", "Usuario o contrasena incorrectos.");
            return null;
        }
        ExternalContext ec = FacesContext.getCurrentInstance().getExternalContext();
        HttpServletRequest req = (HttpServletRequest) ec.getRequest();
        req.changeSessionId();                        // evita fijacion de sesion
        usuario = encontrado.get();
        req.getSession().setAttribute(ATRIBUTO_USUARIO, usuario);
        return "/app/lecturas?faces-redirect=true";
    }

    public String cerrarSesion() {
        ExternalContext ec = FacesContext.getCurrentInstance().getExternalContext();
        HttpSession session = (HttpSession) ec.getSession(false);
        if (session != null) {
            session.invalidate();
        }
        usuario = null;
        return "/login?faces-redirect=true&salida=1";
    }

    public boolean isAutenticado() {
        return usuario != null;
    }

    public String getNombre() {
        return usuario == null ? null : usuario.getNombre();
    }

    public String getRol() {
        return usuario == null ? null : usuario.getRol();
    }

    /** Uso desde EL: #{sesion.puede('REGISTRAR_LECTURA')} */
    public boolean puede(String permiso) {
        try {
            return usuario != null && Permisos.tiene(usuario.getRol(), Permiso.valueOf(permiso));
        } catch (IllegalArgumentException e) {
            return false;
        }
    }

    public boolean puede(Permiso permiso) {
        return usuario != null && Permisos.tiene(usuario.getRol(), permiso);
    }

    public String getNombreUsuario() {
        return nombreUsuario;
    }

    public void setNombreUsuario(String nombreUsuario) {
        this.nombreUsuario = nombreUsuario;
    }

    public String getContrasena() {
        return contrasena;
    }

    public void setContrasena(String contrasena) {
        this.contrasena = contrasena;
    }
}
