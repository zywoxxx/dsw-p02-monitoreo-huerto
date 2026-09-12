package mx.uv.dsw.huerto.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.util.List;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import mx.uv.dsw.huerto.model.Sensor;

/**
 * Pruebas unitarias de RF03 (validacion de lecturas) y RF06 (clasificacion de alerta).
 * No requieren Tomcat ni PostgreSQL: demuestran las reglas, no la persistencia.
 */
class LecturaValidatorTest {

    private static Sensor sensorTemperatura() {
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
    @DisplayName("Positiva: valor numerico dentro de rango fisico y umbral -> sin errores ni alerta")
    void valorValidoEnRango() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        Long sensorId = LecturaValidator.parseSensorId("1", errores);
        BigDecimal valor = LecturaValidator.parseValor("24.5", errores);
        assertEquals(1L, sensorId);
        assertEquals(new BigDecimal("24.5"), valor);
        Sensor s = sensorTemperatura();
        LecturaValidator.validarRangoFisico(s, valor, errores);
        assertTrue(errores.isEmpty(), "no debe haber errores: " + errores);
        assertNull(LecturaValidator.nivelAlerta(s, valor));
    }

    @Test
    @DisplayName("Positiva: valor dentro del rango fisico pero sobre el umbral -> alerta ALTA")
    void valorSobreUmbralGeneraAlertaAlta() {
        Sensor s = sensorTemperatura();
        BigDecimal valor = new BigDecimal("38.00");
        List<String> errores = LecturaValidator.nuevaListaErrores();
        LecturaValidator.validarRangoFisico(s, valor, errores);
        assertTrue(errores.isEmpty());
        assertEquals("ALTA", LecturaValidator.nivelAlerta(s, valor));
        assertTrue(LecturaValidator.mensajeAlerta(s, valor, "ALTA").contains("por encima del maximo 32.00"));
    }

    @Test
    @DisplayName("Positiva: valor bajo el umbral minimo -> alerta BAJA")
    void valorBajoUmbralGeneraAlertaBaja() {
        Sensor s = sensorTemperatura();
        assertEquals("BAJA", LecturaValidator.nivelAlerta(s, new BigDecimal("10.00")));
    }

    @Test
    @DisplayName("Negativa: valor vacio -> error obligatorio")
    void valorVacio() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertNull(LecturaValidator.parseValor("   ", errores));
        assertEquals(1, errores.size());
        assertTrue(errores.get(0).contains("obligatorio"));
    }

    @Test
    @DisplayName("Negativa: valor no numerico -> error de formato")
    void valorNoNumerico() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertNull(LecturaValidator.parseValor("abc", errores));
        assertTrue(errores.get(0).contains("numerico"));
    }

    @Test
    @DisplayName("Negativa: mas de dos decimales -> rechazado")
    void valorConTresDecimales() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertNull(LecturaValidator.parseValor("24.555", errores));
        assertTrue(errores.get(0).contains("decimales"));
    }

    @Test
    @DisplayName("Negativa: valor fuera del rango fisico del tipo de sensor -> rechazado")
    void valorFueraDeRangoFisico() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        LecturaValidator.validarRangoFisico(sensorTemperatura(), new BigDecimal("150"), errores);
        assertEquals(1, errores.size());
        assertTrue(errores.get(0).contains("fuera del rango fisico"));
    }

    @Test
    @DisplayName("Negativa: sensor no seleccionado o id invalido -> error")
    void sensorInvalido() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertNull(LecturaValidator.parseSensorId("", errores));
        assertNull(LecturaValidator.parseSensorId("x", errores));
        assertNull(LecturaValidator.parseSensorId("-3", errores));
        assertEquals(3, errores.size());
    }

    @Test
    @DisplayName("Negativa: sensor inactivo no admite lecturas")
    void sensorInactivo() {
        Sensor s = sensorTemperatura();
        s.setActivo(false);
        List<String> errores = LecturaValidator.nuevaListaErrores();
        LecturaValidator.validarRangoFisico(s, new BigDecimal("20"), errores);
        assertTrue(errores.get(0).contains("inactivo"));
    }

    @Test
    @DisplayName("Negativa: observacion mayor a 200 caracteres -> rechazada")
    void observacionLarga() {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        assertNull(LecturaValidator.parseObservacion("x".repeat(201), errores));
        assertEquals(1, errores.size());
    }
}
