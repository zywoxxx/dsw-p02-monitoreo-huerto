package mx.uv.dsw.huerto.api.seguridad;

import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;

import javax.annotation.PostConstruct;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

import org.springframework.stereotype.Service;

/**
 * Verifica usuario y contrasena contra usuarios.properties (hash PBKDF2-HMAC-SHA256 con sal), igual
 * que en P03. Los usuarios son ficticios y no se agrega una entidad al modelo de siete tablas.
 */
@Service
public class CredencialesService {

    private static final String RECURSO = "/usuarios.properties";

    /** usuario -> [rol, iteraciones, salt hex, hash hex] */
    private final Map<String, String[]> usuarios = new HashMap<>();

    @PostConstruct
    void cargar() throws IOException {
        try (InputStream in = CredencialesService.class.getResourceAsStream(RECURSO)) {
            if (in == null) {
                throw new IllegalStateException("No se encontro " + RECURSO);
            }
            Properties p = new Properties();
            p.load(in);
            for (String nombre : p.stringPropertyNames()) {
                String[] partes = p.getProperty(nombre).trim().split(":");
                if (partes.length == 4 && Permisos.esRolValido(partes[0])) {
                    usuarios.put(nombre.trim().toLowerCase(), partes);
                }
            }
        }
    }

    /** Rol del usuario si las credenciales coinciden; vacio en cualquier otro caso. */
    public Optional<String> rolSiCoincide(String usuario, String contrasena) {
        if (usuario == null || contrasena == null || usuario.isBlank() || contrasena.isEmpty()) {
            return Optional.empty();
        }
        String[] datos = usuarios.get(usuario.trim().toLowerCase());
        if (datos == null) {
            derivar(contrasena, new byte[16], 120000);   // mismo costo aunque el usuario no exista
            return Optional.empty();
        }
        byte[] obtenido = derivar(contrasena, hex(datos[2]), Integer.parseInt(datos[1]));
        return obtenido != null && MessageDigest.isEqual(hex(datos[3]), obtenido)
            ? Optional.of(datos[0]) : Optional.empty();
    }

    private static byte[] derivar(String contrasena, byte[] salt, int iteraciones) {
        try {
            PBEKeySpec spec = new PBEKeySpec(contrasena.toCharArray(), salt, iteraciones, 256);
            return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();
        } catch (Exception e) {
            return null;
        }
    }

    private static byte[] hex(String h) {
        byte[] out = new byte[h.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(h.substring(2 * i, 2 * i + 2), 16);
        }
        return out;
    }
}
