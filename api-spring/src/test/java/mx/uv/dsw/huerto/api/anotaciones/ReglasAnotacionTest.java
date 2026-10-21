package mx.uv.dsw.huerto.api.anotaciones;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import mx.uv.dsw.huerto.api.error.ApiError;

/** El texto se recorta antes de medirlo; zona obligatoria y lectura opcional pero positiva. */
class ReglasAnotacionTest {

    private static AnotacionRequest peticion(Long zonaId, Long lecturaId, String texto) {
        AnotacionRequest r = new AnotacionRequest();
        r.setZonaId(zonaId);
        r.setLecturaId(lecturaId);
        r.setTexto(texto);
        return r;
    }

    @Test
    @DisplayName("Positiva: zona, texto de 3 a 300 caracteres y lectura opcional")
    void valida() {
        assertTrue(ReglasAnotacion.validarForma(peticion(1L, null, "Riego manual por la tarde.")).isEmpty());
        assertTrue(ReglasAnotacion.validarForma(peticion(1L, 12L, "abc")).isEmpty());
        assertTrue(ReglasAnotacion.validarForma(peticion(2L, null, "x".repeat(300))).isEmpty());
    }

    @Test
    @DisplayName("Negativa: texto de 2 caracteres")
    void textoCorto() {
        List<ApiError.Campo> errores = ReglasAnotacion.validarForma(peticion(1L, null, "ok"));
        assertEquals(1, errores.size());
        assertEquals("texto", errores.get(0).getCampo());
        assertEquals("La anotacion debe tener al menos 3 caracteres.", errores.get(0).getMensaje());
    }

    @Test
    @DisplayName("Negativa: texto de 301 caracteres")
    void textoLargo() {
        List<ApiError.Campo> errores = ReglasAnotacion.validarForma(peticion(1L, null, "x".repeat(301)));
        assertEquals(1, errores.size());
        assertEquals("texto", errores.get(0).getCampo());
        assertEquals("La anotacion no puede exceder 300 caracteres.", errores.get(0).getMensaje());
    }

    @Test
    @DisplayName("Negativa: '   ab   ' queda corto al recortar; '  abc  ' es valido")
    void textoConEspacios() {
        List<ApiError.Campo> errores = ReglasAnotacion.validarForma(peticion(1L, null, "   ab   "));
        assertEquals(1, errores.size());
        assertEquals("texto", errores.get(0).getCampo());
        assertTrue(ReglasAnotacion.validarForma(peticion(1L, null, "  abc  ")).isEmpty());
    }

    @Test
    @DisplayName("Negativa: zona ausente o no positiva")
    void zonaAusente() {
        assertEquals("zonaId", ReglasAnotacion.validarForma(peticion(null, null, "texto valido")).get(0).getCampo());
        assertEquals("zonaId", ReglasAnotacion.validarForma(peticion(0L, null, "texto valido")).get(0).getCampo());
    }

    @Test
    @DisplayName("Negativa: lectura indicada pero <= 0")
    void lecturaNoPositiva() {
        List<ApiError.Campo> errores = ReglasAnotacion.validarForma(peticion(1L, -3L, "texto valido"));
        assertEquals(1, errores.size());
        assertEquals("lecturaId", errores.get(0).getCampo());
        assertEquals(1, ReglasAnotacion.validarForma(peticion(1L, 0L, "texto valido")).size());
    }

    @Test
    @DisplayName("Negativa: sin zona, lectura 0 y sin texto -> tres errores juntos")
    void formaIncompleta() {
        assertEquals(3, ReglasAnotacion.validarForma(peticion(null, 0L, null)).size());
    }
}
