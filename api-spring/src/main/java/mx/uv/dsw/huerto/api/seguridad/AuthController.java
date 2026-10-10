package mx.uv.dsw.huerto.api.seguridad;

import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import mx.uv.dsw.huerto.api.error.ApiError;
import mx.uv.dsw.huerto.api.error.ApiException;

/** POST /api/auth/login : cambia credenciales por un token con el rol. No hay registro ni recuperacion. */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    /** Cuerpo de la peticion de acceso. */
    public static class Credenciales {
        private String usuario;
        private String contrasena;

        public String getUsuario() {
            return usuario;
        }

        public void setUsuario(String usuario) {
            this.usuario = usuario;
        }

        public String getContrasena() {
            return contrasena;
        }

        public void setContrasena(String contrasena) {
            this.contrasena = contrasena;
        }
    }

    private final CredencialesService credenciales;
    private final TokenService tokens;

    public AuthController(CredencialesService credenciales, TokenService tokens) {
        this.credenciales = credenciales;
        this.tokens = tokens;
    }

    @PostMapping("/login")
    public Map<String, Object> login(@RequestBody Credenciales c) {
        List<ApiError.Campo> faltan = new ArrayList<>();
        if (c.getUsuario() == null || c.getUsuario().trim().isEmpty()) {
            faltan.add(new ApiError.Campo("usuario", "El usuario es obligatorio."));
        }
        if (c.getContrasena() == null || c.getContrasena().isEmpty()) {
            faltan.add(new ApiError.Campo("contrasena", "La contrasena es obligatoria."));
        }
        if (!faltan.isEmpty()) {
            throw ApiException.validacion(faltan);
        }
        String rol = credenciales.rolSiCoincide(c.getUsuario(), c.getContrasena())
            .orElseThrow(() -> ApiException.noAutenticado("Usuario o contrasena incorrectos."));
        String usuario = c.getUsuario().trim().toLowerCase();
        Map<String, Object> r = new LinkedHashMap<>();
        r.put("token", tokens.emitir(usuario, rol));
        r.put("tipo", "Bearer");
        r.put("usuario", usuario);
        r.put("rol", rol);
        r.put("expiraEn", OffsetDateTime.now().plusMinutes(tokens.getMinutos()));
        return r;
    }
}
