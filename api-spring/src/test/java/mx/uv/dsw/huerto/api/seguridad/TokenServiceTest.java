package mx.uv.dsw.huerto.api.seguridad;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** El token solo vale si la firma es correcta, el rol es uno de los tres y no ha caducado. */
class TokenServiceTest {

    private static final Instant AHORA = Instant.parse("2026-09-29T18:00:00Z");

    private static final String SECRETO = "secreto-de-prueba-de-32-caracteres-o-mas";

    private static TokenService servicio(String secreto, Instant instante) {
        return new TokenService(secreto, 30, Clock.fixed(instante, ZoneOffset.UTC));
    }

    @Test
    @DisplayName("Positiva: un token emitido se valida y devuelve usuario y rol")
    void emitirYValidar() {
        TokenService s = servicio(SECRETO, AHORA);
        UsuarioAutenticado u = s.validar(s.emitir("observador", "OBSERVADOR")).orElseThrow();
        assertEquals("observador", u.getNombre());
        assertEquals("OBSERVADOR", u.getRol());
    }

    @Test
    @DisplayName("Negativa: token caducado")
    void caducado() {
        String token = servicio(SECRETO, AHORA).emitir("observador", "OBSERVADOR");
        TokenService despues = servicio(SECRETO, AHORA.plus(Duration.ofMinutes(31)));
        assertTrue(despues.validar(token).isEmpty());
    }

    @Test
    @DisplayName("Negativa: firma alterada, otro secreto, rol inventado o texto que no es token")
    void invalidos() {
        TokenService s = servicio(SECRETO, AHORA);
        String token = s.emitir("observador", "OBSERVADOR");
        assertTrue(s.validar(token.substring(0, token.length() - 2) + "xx").isEmpty());
        assertTrue(servicio("otro-secreto-distinto-de-32-caracteres", AHORA).validar(token).isEmpty());
        assertTrue(s.validar(s.emitir("alguien", "ADMIN")).isEmpty());
        assertTrue(s.validar("no-es-un-token").isEmpty());
        assertTrue(s.validar(null).isEmpty());
    }

    @Test
    @DisplayName("Negativa: un secreto de menos de 32 caracteres impide arrancar")
    void secretoCortoSeRechaza() {
        assertThrows(IllegalStateException.class, () -> servicio("corto", AHORA));
    }
}
