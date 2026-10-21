package mx.uv.dsw.huerto.api.alertas;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import mx.uv.dsw.huerto.api.error.ApiError;
import mx.uv.dsw.huerto.api.error.ApiException;
import mx.uv.dsw.huerto.api.error.ApiExceptionHandler;
import mx.uv.dsw.huerto.api.lecturas.Pagina;
import mx.uv.dsw.huerto.api.seguridad.TokenFilter;
import mx.uv.dsw.huerto.api.seguridad.TokenService;

/**
 * Contrato HTTP de /api/alertas sin base de datos: el servicio se simula y se comprueba que cada
 * situacion responde con el estado y el cuerpo que promete openapi.yaml.
 */
@WebMvcTest(AlertaController.class)
@Import({TokenService.class, TokenFilter.class, ApiExceptionHandler.class})
@TestPropertySource(properties = {"huerto.jwt.secreto=secreto-de-prueba-de-32-caracteres-o-mas", "huerto.jwt.minutos=30",
    "huerto.cors.origen=http://localhost:4200"})
class AlertaControllerTest {

    @Autowired
    private MockMvc mvc;

    @Autowired
    private TokenService tokens;

    @MockBean
    private AlertaService servicio;

    private String bearer(String rol) {
        return "Bearer " + tokens.emitir(rol.toLowerCase(), rol);
    }

    private static Alerta alerta(long id, boolean atendida, String atendidaPor) {
        Alerta a = new Alerta();
        a.setId(id);
        a.setLecturaId(38);
        a.setSensorCodigo("SEN-A-TEMP-01");
        a.setVariable("Temperatura ambiente");
        a.setZonaId(1);
        a.setZona("Cama A");
        a.setValor(new BigDecimal("38.00"));
        a.setUnidad("C");
        a.setNivel("ALTA");
        a.setMensaje("mensaje");
        a.setAtendida(atendida);
        if (atendida) {
            a.setAtendidaEn(OffsetDateTime.now());
            a.setAtendidaPor(atendidaPor);
        }
        a.setCreadaEn(OffsetDateTime.now());
        return a;
    }

    @Test
    @DisplayName("401 sin token, al consultar y al cambiar estado")
    void sinToken() throws Exception {
        mvc.perform(get("/api/alertas")).andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.codigo").value("NO_AUTENTICADO"));
        mvc.perform(patch("/api/alertas/7").contentType(MediaType.APPLICATION_JSON).content("{\"atendida\":true}"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("200 GET con cualquier rol; una alerta pendiente no lleva atendidaEn ni atendidaPor")
    void listar() throws Exception {
        when(servicio.listar(any(), any(), any(), any(Integer.class), any(Integer.class)))
            .thenReturn(new Pagina<>(List.of(alerta(7, false, null)), 0, 10, 1));
        mvc.perform(get("/api/alertas").header("Authorization", bearer("OBSERVADOR")))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.total").value(1))
            .andExpect(jsonPath("$.contenido[0].nivel").value("ALTA"))
            .andExpect(jsonPath("$.contenido[0].atendida").value(false))
            .andExpect(jsonPath("$.contenido[0].atendidaEn").doesNotExist())
            .andExpect(jsonPath("$.contenido[0].atendidaPor").doesNotExist());
    }

    @Test
    @DisplayName("403 PATCH con OBSERVADOR y con COORDINACION; el servicio no se llama")
    void rolSinPermiso() throws Exception {
        for (String rol : List.of("OBSERVADOR", "COORDINACION")) {
            mvc.perform(patch("/api/alertas/7").header("Authorization", bearer(rol))
                    .contentType(MediaType.APPLICATION_JSON).content("{\"atendida\":true}"))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.codigo").value("ROL_SIN_PERMISO"));
        }
        verify(servicio, never()).cambiarAtencion(anyLong(), any(), any());
    }

    @Test
    @DisplayName("200 PATCH del responsable: el rol que recibe el servicio es el del token")
    void atender() throws Exception {
        when(servicio.cambiarAtencion(7L, true, "RESPONSABLE")).thenReturn(alerta(7, true, "RESPONSABLE"));
        mvc.perform(patch("/api/alertas/7").header("Authorization", bearer("RESPONSABLE"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"atendida\":true}"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(7))
            .andExpect(jsonPath("$.atendida").value(true))
            .andExpect(jsonPath("$.atendidaPor").value("RESPONSABLE"))
            .andExpect(jsonPath("$.atendidaEn").exists());
    }

    @Test
    @DisplayName("400 con cuerpo {} (atendida ausente llega como null) y con atendida no booleana")
    void cuerpoInvalido() throws Exception {
        when(servicio.cambiarAtencion(7L, null, "RESPONSABLE"))
            .thenThrow(ApiException.validacion(List.of(new ApiError.Campo("atendida", "Indica atendida: true o false."))));
        mvc.perform(patch("/api/alertas/7").header("Authorization", bearer("RESPONSABLE"))
                .contentType(MediaType.APPLICATION_JSON).content("{}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.codigo").value("VALIDACION"))
            .andExpect(jsonPath("$.errores[0].campo").value("atendida"));

        mvc.perform(patch("/api/alertas/7").header("Authorization", bearer("RESPONSABLE"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"atendida\":\"si\"}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.codigo").value("VALIDACION"));
    }

    @Test
    @DisplayName("404 y 409 segun lo que reporte el servicio")
    void erroresDelServicio() throws Exception {
        when(servicio.porId(999L)).thenThrow(ApiException.noEncontrado("La alerta 999 no existe."));
        mvc.perform(get("/api/alertas/999").header("Authorization", bearer("COORDINACION")))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.codigo").value("NO_ENCONTRADO"))
            .andExpect(jsonPath("$.mensaje").value("La alerta 999 no existe."));

        when(servicio.cambiarAtencion(999L, true, "RESPONSABLE")).thenThrow(ApiException.noEncontrado("La alerta 999 no existe."));
        mvc.perform(patch("/api/alertas/999").header("Authorization", bearer("RESPONSABLE"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"atendida\":true}"))
            .andExpect(status().isNotFound());

        when(servicio.cambiarAtencion(7L, true, "RESPONSABLE")).thenThrow(ApiException.conflicto("La alerta 7 ya estaba atendida."));
        mvc.perform(patch("/api/alertas/7").header("Authorization", bearer("RESPONSABLE"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"atendida\":true}"))
            .andExpect(status().isConflict())
            .andExpect(jsonPath("$.codigo").value("CONFLICTO"))
            .andExpect(jsonPath("$.mensaje").value("La alerta 7 ya estaba atendida."));
    }
}
