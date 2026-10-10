package mx.uv.dsw.huerto.api.salud;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/** GET /api/health : 200 si la API conecta a PostgreSQL, 503 si no. Publica y sin credenciales. */
@RestController
public class HealthController {

    private final JdbcTemplate jdbc;

    public HealthController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @GetMapping("/api/health")
    public ResponseEntity<Map<String, Object>> salud() {
        Map<String, Object> r = new LinkedHashMap<>();
        r.put("app", "huerto-api PR09 (P04 Spring Boot)");
        try {
            String version = jdbc.queryForObject("SELECT version()", String.class);
            Long lecturas = jdbc.queryForObject("SELECT count(*) FROM lectura", Long.class);
            r.put("status", "UP");
            r.put("db", "UP");
            r.put("postgres", soloVersion(version));
            r.put("lecturas", lecturas);
            return ResponseEntity.ok(r);
        } catch (Exception e) {
            r.put("status", "DOWN");
            r.put("db", "DOWN");
            r.put("error", "PostgreSQL no responde");
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(r);
        }
    }

    /** "PostgreSQL 16.15 (Debian ...) on x86_64..." se reduce a "PostgreSQL 16.15": no se publica la plataforma. */
    static String soloVersion(String version) {
        if (version == null) {
            return "";
        }
        String[] partes = version.trim().split(" ");
        return partes.length >= 2 ? partes[0] + " " + partes[1] : version.trim();
    }
}
