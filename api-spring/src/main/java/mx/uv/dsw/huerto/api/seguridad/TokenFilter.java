package mx.uv.dsw.huerto.api.seguridad;

import java.io.IOException;
import java.util.Optional;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import com.fasterxml.jackson.databind.ObjectMapper;

import mx.uv.dsw.huerto.api.error.ApiError;

/**
 * Exige "Authorization: Bearer <token>" en /api/**, salvo la salud y el inicio de sesion.
 * Las peticiones OPTIONS (preflight de CORS) pasan sin token porque el navegador no lo envia en ellas.
 */
@Component
@Order(Ordered.LOWEST_PRECEDENCE - 10)
public class TokenFilter extends OncePerRequestFilter {

    private final TokenService tokens;
    private final ObjectMapper json;

    public TokenFilter(TokenService tokens, ObjectMapper json) {
        this.tokens = tokens;
        this.json = json;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String ruta = request.getRequestURI().substring(request.getContextPath().length());
        return !ruta.startsWith("/api/")
            || ruta.equals("/api/health")
            || ruta.equals("/api/auth/login")
            || "OPTIONS".equalsIgnoreCase(request.getMethod());
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String cabecera = request.getHeader("Authorization");
        Optional<UsuarioAutenticado> usuario = cabecera != null && cabecera.startsWith("Bearer ")
            ? tokens.validar(cabecera.substring(7).trim()) : Optional.empty();
        if (usuario.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            response.setCharacterEncoding("UTF-8");
            response.setHeader("WWW-Authenticate", "Bearer");
            json.writeValue(response.getWriter(), new ApiError("NO_AUTENTICADO",
                "Falta el token, es invalido o ya caduco. Inicia sesion de nuevo."));
            return;
        }
        request.setAttribute(UsuarioAutenticado.ATRIBUTO, usuario.get());
        chain.doFilter(request, response);
    }
}
