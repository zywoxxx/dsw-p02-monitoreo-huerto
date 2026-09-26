package mx.uv.dsw.huerto.model;

import java.io.Serializable;

/** Persona autenticada en la sesion: nombre de usuario y rol funcional del PR09. */
public class Usuario implements Serializable {

    private static final long serialVersionUID = 1L;

    private final String nombre;
    private final String rol;

    public Usuario(String nombre, String rol) {
        this.nombre = nombre;
        this.rol = rol;
    }

    public String getNombre() {
        return nombre;
    }

    public String getRol() {
        return rol;
    }
}
