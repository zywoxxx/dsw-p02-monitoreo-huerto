package mx.uv.dsw.huerto.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Properties;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** Pruebas del control de acceso de P03: hash con sal, credenciales invalidas y roles permitidos. */
class AuthServiceTest {

    private static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) {
            sb.append(String.format("%02x", x));
        }
        return sb.toString();
    }

    private static AuthService servicioConUsuario(String usuario, String rol, String contrasena) {
        byte[] salt = new byte[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
        int iteraciones = 1000; // pocas iteraciones para que la prueba sea rapida
        String hash = hex(AuthService.derivar(contrasena, salt, iteraciones));
        Properties p = new Properties();
        p.setProperty(usuario, rol + ":" + iteraciones + ":" + hex(salt) + ":" + hash);
        AuthService s = new AuthService();
        s.cargarDesde(p);
        return s;
    }

    @Test
    @DisplayName("Positiva: usuario y contrasena correctos devuelven el rol")
    void credencialesCorrectas() {
        AuthService s = servicioConUsuario("observador", "OBSERVADOR", "Clave#1");
        assertEquals("OBSERVADOR", s.autenticar("observador", "Clave#1").orElseThrow().getRol());
        assertEquals("OBSERVADOR", s.autenticar("  Observador ", "Clave#1").orElseThrow().getRol());
    }

    @Test
    @DisplayName("Negativa: contrasena incorrecta, usuario inexistente o vacios no autentican")
    void credencialesIncorrectas() {
        AuthService s = servicioConUsuario("observador", "OBSERVADOR", "Clave#1");
        assertTrue(s.autenticar("observador", "clave#1").isEmpty());
        assertTrue(s.autenticar("otro", "Clave#1").isEmpty());
        assertTrue(s.autenticar("", "Clave#1").isEmpty());
        assertTrue(s.autenticar("observador", "").isEmpty());
        assertTrue(s.autenticar(null, null).isEmpty());
    }

    @Test
    @DisplayName("Negativa: un rol fuera de los tres funcionales se ignora al cargar")
    void rolNoPermitidoSeIgnora() {
        AuthService s = servicioConUsuario("admin", "ADMIN", "Clave#1");
        assertTrue(s.autenticar("admin", "Clave#1").isEmpty());
    }

    @Test
    @DisplayName("Permisos por rol segun el acta: solo el observador registra lecturas; los tres anotan")
    void permisosPorRol() {
        assertTrue(Permisos.tiene("OBSERVADOR", Permisos.Permiso.REGISTRAR_LECTURA));
        assertFalse(Permisos.tiene("RESPONSABLE", Permisos.Permiso.REGISTRAR_LECTURA));
        assertFalse(Permisos.tiene("COORDINACION", Permisos.Permiso.REGISTRAR_LECTURA));
        assertTrue(Permisos.tiene("RESPONSABLE", Permisos.Permiso.ANOTAR));
        assertTrue(Permisos.tiene("COORDINACION", Permisos.Permiso.CONSULTAR));
        assertFalse(Permisos.tiene(null, Permisos.Permiso.CONSULTAR));
    }
}
