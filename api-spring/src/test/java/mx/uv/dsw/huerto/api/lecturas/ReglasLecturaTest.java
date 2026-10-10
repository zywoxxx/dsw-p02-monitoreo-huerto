package mx.uv.dsw.huerto.api.lecturas;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import mx.uv.dsw.huerto.api.sensores.Sensor;

/** Las reglas del huerto deben comportarse igual que en P02/P03. */
class ReglasLecturaTest {

    private static Sensor temperatura() {
        Sensor s = new Sensor();
        s.setId(1);
        s.setCodigo("SEN-A-TEMP-01");
        s.setActivo(true);
        s.setZona("Cama A");
        s.setVariable("Temperatura ambiente");
        s.setUnidad("C");
        s.setRangoFisicoMinimo(new BigDecimal("-10.00"));
        s.setRangoFisicoMaximo(new BigDecimal("60.00"));
        s.setUmbralMinimo(new BigDecimal("15.00"));
        s.setUmbralMaximo(new BigDecimal("32.00"));
        return s;
    }

    private static LecturaRequest peticion(Long sensorId, String valor, String observacion) {
        LecturaRequest r = new LecturaRequest();
        r.setSensorId(sensorId);
        r.setValor(valor == null ? null : new BigDecimal(valor));
        r.setObservacion(observacion);
        return r;
    }

    @Test
    @DisplayName("Positiva: 25.5 es valida en forma, rango y umbral")
    void valida() {
        assertTrue(ReglasLectura.validarForma(peticion(1L, "25.5", "ok")).isEmpty());
        assertTrue(ReglasLectura.dentroDelRangoFisico(temperatura(), new BigDecimal("25.5")));
        assertNull(ReglasLectura.nivelAlerta(temperatura(), new BigDecimal("25.5")));
    }

    @Test
    @DisplayName("Alertas: 38 -> ALTA, 10 -> BAJA, 15 y 32 (limites) -> sin alerta")
    void alertas() {
        Sensor s = temperatura();
        assertEquals("ALTA", ReglasLectura.nivelAlerta(s, new BigDecimal("38")));
        assertEquals("BAJA", ReglasLectura.nivelAlerta(s, new BigDecimal("10")));
        assertNull(ReglasLectura.nivelAlerta(s, new BigDecimal("15")));
        assertNull(ReglasLectura.nivelAlerta(s, new BigDecimal("32.00")));
        assertTrue(ReglasLectura.mensajeAlerta(s, new BigDecimal("38"), "ALTA").contains("por encima del maximo 32.00"));
    }

    @Test
    @DisplayName("Negativa: 150 esta fuera del rango fisico; -10 y 60 son limites validos")
    void rangoFisico() {
        Sensor s = temperatura();
        assertFalse(ReglasLectura.dentroDelRangoFisico(s, new BigDecimal("150")));
        assertTrue(ReglasLectura.dentroDelRangoFisico(s, new BigDecimal("-10")));
        assertTrue(ReglasLectura.dentroDelRangoFisico(s, new BigDecimal("60")));
    }

    @Test
    @DisplayName("Negativa: 24.555 se rechaza por decimales; no se redondea")
    void decimales() {
        assertEquals("valor", ReglasLectura.validarForma(peticion(1L, "24.555", null)).get(0).getCampo());
        assertTrue(ReglasLectura.validarForma(peticion(1L, "24.55", null)).isEmpty());
    }

    @Test
    @DisplayName("Negativa: sin sensor, sin valor y observacion de 201 caracteres -> tres errores")
    void formaIncompleta() {
        assertEquals(3, ReglasLectura.validarForma(peticion(null, null, "x".repeat(201))).size());
        assertEquals(1, ReglasLectura.validarForma(peticion(-3L, "20", null)).size());
    }
}
