package mx.uv.dsw.huerto.service;

import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidKeySpecException;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;

import javax.annotation.PostConstruct;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import javax.enterprise.context.ApplicationScoped;

import mx.uv.dsw.huerto.model.Usuario;

/**
 * Autenticacion minima para P03: usuarios ficticios en usuarios.properties con contrasena
 * almacenada como hash PBKDF2-HMAC-SHA256 con sal. No hay registro publico ni recuperacion de
 * contrasena (no estan en el alcance aprobado) y no se agrega una entidad al modelo de datos.
 */
@ApplicationScoped
public class AuthService {

    private static final String RECURSO = "/usuarios.properties";
    private static final int LONGITUD_BITS = 256;

    /** usuario -> [rol, iteraciones, salt hex, hash hex] */
    private final Map<String, String[]> usuarios = new HashMap<>();

    @PostConstruct
    public void cargar() {
        try (InputStream in = AuthService.class.getResourceAsStream(RECURSO)) {
            if (in == null) {
                throw new IllegalStateException("No se encontro " + RECURSO + " en el WAR");
            }
            Properties p = new Properties();
            p.load(in);
            cargarDesde(p);
        } catch (IOException e) {
            throw new IllegalStateException("No fue posible leer " + RECURSO, e);
        }
    }

    /** Separado para poder probarlo con JUnit sin recursos del WAR. */
    void cargarDesde(Properties p) {
        usuarios.clear();
        for (String nombre : p.stringPropertyNames()) {
            String[] partes = p.getProperty(nombre).trim().split(":");
            if (partes.length == 4 && Permisos.esRolValido(partes[0])) {
                usuarios.put(nombre.trim().toLowerCase(), partes);
            }
        }
    }

    /** Devuelve el usuario si las credenciales coinciden; vacio en cualquier otro caso. */
    public Optional<Usuario> autenticar(String nombre, String contrasena) {
        if (nombre == null || contrasena == null || nombre.isBlank() || contrasena.isEmpty()) {
            return Optional.empty();
        }
        String[] datos = usuarios.get(nombre.trim().toLowerCase());
        if (datos == null) {
            // se calcula un hash de todos modos para no revelar por tiempo si el usuario existe
            derivar(contrasena, new byte[16], 120000);
            return Optional.empty();
        }
        byte[] salt = hexABytes(datos[2]);
        byte[] esperado = hexABytes(datos[3]);
        byte[] obtenido = derivar(contrasena, salt, Integer.parseInt(datos[1]));
        if (obtenido != null && MessageDigest.isEqual(esperado, obtenido)) {
            return Optional.of(new Usuario(nombre.trim().toLowerCase(), datos[0]));
        }
        return Optional.empty();
    }

    static byte[] derivar(String contrasena, byte[] salt, int iteraciones) {
        try {
            PBEKeySpec spec = new PBEKeySpec(contrasena.toCharArray(), salt, iteraciones, LONGITUD_BITS);
            return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();
        } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
            return null;
        }
    }

    static byte[] hexABytes(String hex) {
        byte[] out = new byte[hex.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(hex.substring(2 * i, 2 * i + 2), 16);
        }
        return out;
    }
}
