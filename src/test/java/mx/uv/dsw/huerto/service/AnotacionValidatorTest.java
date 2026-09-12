package mx.uv.dsw.huerto.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** Pruebas unitarias de RF06 (anotaciones) y de los tres roles funcionales del PR09. */
class AnotacionValidatorTest {

    @Test
    @DisplayName("Positiva: zona, rol valido y texto dentro de limites")
    void anotacionValida() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertEquals(1L, AnotacionValidator.parseZonaId("1", errores));
        assertNull(AnotacionValidator.parseLecturaId("", errores));
        assertEquals("OBSERVADOR", AnotacionValidator.parseRol("observador", errores));
        assertEquals("Hojas con manchas", AnotacionValidator.parseTexto("  Hojas con manchas ", errores));
        assertTrue(errores.isEmpty(), errores.toString());
    }

    @Test
    @DisplayName("Negativa: rol fuera de los tres roles funcionales")
    void rolInvalido() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertNull(AnotacionValidator.parseRol("ADMIN", errores));
        assertEquals(1, errores.size());
        assertTrue(errores.get(0).contains("no es valido"));
    }

    @Test
    @DisplayName("Negativa: texto vacio o demasiado largo")
    void textoInvalido() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertNull(AnotacionValidator.parseTexto("  ", errores));
        assertNull(AnotacionValidator.parseTexto("x".repeat(301), errores));
        assertEquals(2, errores.size());
    }

    @Test
    @DisplayName("Negativa: zona vacia y lectura no numerica")
    void zonaYLecturaInvalidas() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertNull(AnotacionValidator.parseZonaId("", errores));
        assertNull(AnotacionValidator.parseLecturaId("abc", errores));
        assertEquals(2, errores.size());
    }
}
