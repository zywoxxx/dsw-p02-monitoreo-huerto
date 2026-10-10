package mx.uv.dsw.huerto.api.seguridad;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.Clock;
import java.time.Instant;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Emite y valida tokens con formato JWT (cabecera.carga.firma, HS256) usando solo el JDK y Jackson.
 * La carga lleva usuario (sub), rol y caducidad (exp). La API no guarda sesion: cada peticion se
 * autentica con su token.
 */
@Service
public class TokenService {

    private static final Logger LOG = LoggerFactory.getLogger(TokenService.class);
    private static final String CABECERA = "{\"alg\":\"HS256\",\"typ\":\"JWT\"}";
    private static final Base64.Encoder B64 = Base64.getUrlEncoder().withoutPadding();
    private static final Base64.Decoder B64D = Base64.getUrlDecoder();
    /** HS256 usa claves de 256 bits; un secreto mas corto se rechaza al arrancar. */
    private static final int LARGO_MINIMO = 32;

    private final byte[] secreto;
    private final long minutos;
    private final Clock reloj;
    private final ObjectMapper json = new ObjectMapper();

    @Autowired
    public TokenService(@Value("${huerto.jwt.secreto:}") String secreto, @Value("${huerto.jwt.minutos:30}") long minutos) {
        this(secreto, minutos, Clock.systemUTC());
    }

    TokenService(String secreto, long minutos, Clock reloj) {
        if (secreto == null || secreto.isBlank()) {
            byte[] aleatorio = new byte[32];
            new SecureRandom().nextBytes(aleatorio);
            this.secreto = aleatorio;
            LOG.warn("JWT_SECRET no definido: se genero un secreto temporal; los tokens dejan de valer al reiniciar.");
        } else {
            this.secreto = secreto.getBytes(StandardCharsets.UTF_8);
            if (this.secreto.length < LARGO_MINIMO) {
                throw new IllegalStateException("JWT_SECRET debe tener al menos " + LARGO_MINIMO + " caracteres.");
            }
        }
        this.minutos = minutos;
        this.reloj = reloj;
    }

    public long getMinutos() {
        return minutos;
    }

    public String emitir(String usuario, String rol) {
        try {
            Map<String, Object> carga = new LinkedHashMap<>();
            carga.put("sub", usuario);
            carga.put("rol", rol);
            carga.put("exp", Instant.now(reloj).plusSeconds(minutos * 60).getEpochSecond());
            String base = B64.encodeToString(CABECERA.getBytes(StandardCharsets.UTF_8)) + "."
                + B64.encodeToString(json.writeValueAsBytes(carga));
            return base + "." + B64.encodeToString(firmar(base));
        } catch (Exception e) {
            throw new IllegalStateException("No fue posible emitir el token", e);
        }
    }

    /** Devuelve el usuario si la firma es correcta, el rol es uno de los tres y el token no ha caducado. */
    public Optional<UsuarioAutenticado> validar(String token) {
        try {
            String[] partes = token == null ? new String[0] : token.split("\\.");
            if (partes.length != 3) {
                return Optional.empty();
            }
            byte[] esperada = firmar(partes[0] + "." + partes[1]);
            if (!MessageDigest.isEqual(esperada, B64D.decode(partes[2]))) {
                return Optional.empty();
            }
            Map<String, Object> carga = json.readValue(B64D.decode(partes[1]), new TypeReference<Map<String, Object>>() { });
            long exp = ((Number) carga.get("exp")).longValue();
            String rol = String.valueOf(carga.get("rol"));
            if (Instant.now(reloj).getEpochSecond() >= exp || !Permisos.esRolValido(rol)) {
                return Optional.empty();
            }
            return Optional.of(new UsuarioAutenticado(String.valueOf(carga.get("sub")), rol));
        } catch (Exception e) {
            return Optional.empty();
        }
    }

    private byte[] firmar(String base) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(secreto, "HmacSHA256"));
        return mac.doFinal(base.getBytes(StandardCharsets.UTF_8));
    }
}
