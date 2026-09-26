package mx.uv.dsw.huerto.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.util.List;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import mx.uv.dsw.huerto.model.Sensor;

/** Casos limite agregados en P03: valores exactamente en el umbral y entradas que no deben redondearse. */
class LecturaValidatorLimitesTest {

    private static Sensor temperatura() {
        Sensor s = new Sensor();
        s.setId(1L);
        s.setCodigo("SEN-A-TEMP-01");
        s.setActivo(true);
        s.setZona("Cama A");
        s.setVariableNombre("Temperatura ambiente");
        s.setUnidad("C");
        s.setValorMinimo(new BigDecimal("-10.00"));
        s.setValorMaximo(new BigDecimal("60.00"));
        s.setUmbralMinimo(new BigDecimal("15.00"));
        s.setUmbralMaximo(new BigDecimal("32.00"));
        return s;
    }

    @Test
    @DisplayName("Limite: 15 y 32 coinciden con el umbral y no generan alerta")
    void valoresEnElLimiteNoGeneranAlerta() {
        Sensor s = temperatura();
        assertNull(LecturaValidator.nivelAlerta(s, new BigDecimal("15")));
        assertNull(LecturaValidator.nivelAlerta(s, new BigDecimal("32.00")));
        assertEquals("BAJA", LecturaValidator.nivelAlerta(s, new BigDecimal("14.99")));
        assertEquals("ALTA", LecturaValidator.nivelAlerta(s, new BigDecimal("32.01")));
    }

    @Test
    @DisplayName("Limite: -10 y 60 son fisicamente validos; -10.01 y 60.01 no")
    void limitesDelRangoFisico() {
        Sensor s = temperatura();
        List<String> errores = LecturaValidator.nuevaListaErrores();
        LecturaValidator.validarRangoFisico(s, new BigDecimal("-10"), errores);
        LecturaValidator.validarRangoFisico(s, new BigDecimal("60"), errores);
        assertTrue(errores.isEmpty(), errores.toString());
        LecturaValidator.validarRangoFisico(s, new BigDecimal("-10.01"), errores);
        LecturaValidator.validarRangoFisico(s, new BigDecimal("60.01"), errores);
        assertEquals(2, errores.size());
    }

    @Test
    @DisplayName("Sin redondeo silencioso: 24.555 y 24.550 se rechazan, 24.55 y 24,5 se aceptan")
    void noRedondea() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertNull(LecturaValidator.parseValor("24.555", errores));
        assertNull(LecturaValidator.parseValor("24.550", errores));
        assertEquals(2, errores.size());
        assertEquals(new BigDecimal("24.55"), LecturaValidator.parseValor("24.55", errores));
        assertEquals(new BigDecimal("24.5"), LecturaValidator.parseValor("24,5", errores));
        assertEquals(2, errores.size());
    }
}
