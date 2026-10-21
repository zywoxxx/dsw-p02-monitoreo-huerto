package mx.uv.dsw.huerto.api.anotaciones;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.OffsetDateTime;
import java.util.List;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
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
 * Contrato HTTP de /api/anotaciones sin base de datos: el servicio se simula y se comprueba que cada
 * situacion responde con el estado y el cuerpo que promete openapi.yaml.
 */
@WebMvcTest(AnotacionController.class)
@Import({TokenService.class, TokenFilter.class, ApiExceptionHandler.class})
@TestPropertySource(properties = {"huerto.jwt.secreto=secreto-de-prueba-de-32-caracteres-o-mas", "huerto.jwt.minutos=30",
    "huerto.cors.origen=http://localhost:4200"})
class AnotacionControllerTest {

    @Autowired
    private MockMvc mvc;

    @Autowired
    private TokenService tokens;

    @MockBean
    private AnotacionService servicio;

    private String bearer(String rol) {
        return "Bearer " + tokens.emitir(rol.toLowerCase(), rol);
    }

    private static Anotacion anotacion(long id, String autorRol, Long lecturaId) {
        Anotacion n = new Anotacion();
        n.setId(id);
        n.setZonaId(1);
        n.setZona("Cama A");
        n.setLecturaId(lecturaId);
        n.setAutorRol(autorRol);
        n.setTexto("Riego manual por la tarde.");
        n.setCreadaEn(OffsetDateTime.now());
        return n;
    }

    @Test
    @DisplayName("401 sin token, al consultar y al registrar")
    void sinToken() throws Exception {
        mvc.perform(get("/api/anotaciones")).andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.codigo").value("NO_AUTENTICADO"));
        mvc.perform(post("/api/anotaciones").contentType(MediaType.APPLICATION_JSON)
                .content("{\"zonaId\":1,\"texto\":\"Riego manual por la tarde.\"}"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("200 GET con cualquier rol; sin lectura el campo lecturaId no aparece")
    void listar() throws Exception {
        when(servicio.listar(any(), any(Integer.class), any(Integer.class)))
            .thenReturn(new Pagina<>(List.of(anotacion(1, "RESPONSABLE", null)), 0, 10, 1));
        mvc.perform(get("/api/anotaciones").header("Authorization", bearer("OBSERVADOR")))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.total").value(1))
            .andExpect(jsonPath("$.contenido[0].autorRol").value("RESPONSABLE"))
            .andExpect(jsonPath("$.contenido[0].lecturaId").doesNotExist());
    }

    @Test
    @DisplayName("201 POST con Location; el rol que firma es el del token, no uno del cuerpo")
    void crear() throws Exception {
        when(servicio.registrar(any(), eq("COORDINACION"))).thenReturn(anotacion(5, "COORDINACION", null));
        mvc.perform(post("/api/anotaciones").header("Authorization", bearer("COORDINACION"))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"zonaId\":1,\"texto\":\"Riego manual por la tarde.\",\"autorRol\":\"RESPONSABLE\"}"))
            .andExpect(status().isCreated())
            .andExpect(header().string("Location", "/api/anotaciones/5"))
            .andExpect(jsonPath("$.id").value(5))
            .andExpect(jsonPath("$.autorRol").value("COORDINACION"));

        ArgumentCaptor<AnotacionRequest> peticion = ArgumentCaptor.forClass(AnotacionRequest.class);
        verify(servicio).registrar(peticion.capture(), eq("COORDINACION"));
        assertEquals(1L, peticion.getValue().getZonaId());
        assertNull(peticion.getValue().getLecturaId());
        assertEquals("Riego manual por la tarde.", peticion.getValue().getTexto());
    }

    @Test
    @DisplayName("201 POST del observador con lecturaId")
    void crearSobreLectura() throws Exception {
        when(servicio.registrar(any(), eq("OBSERVADOR"))).thenReturn(anotacion(6, "OBSERVADOR", 12L));
        mvc.perform(post("/api/anotaciones").header("Authorization", bearer("OBSERVADOR"))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"zonaId\":1,\"lecturaId\":12,\"texto\":\"Se revisa el sensor.\"}"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.lecturaId").value(12))
            .andExpect(jsonPath("$.autorRol").value("OBSERVADOR"));
    }

    @Test
    @DisplayName("400 por reglas de forma (texto 'ok') y por JSON con tipos incorrectos")
    void formaInvalida() throws Exception {
        when(servicio.registrar(any(), any()))
            .thenThrow(ApiException.validacion(List.of(new ApiError.Campo("texto", "La anotacion debe tener al menos 3 caracteres."))));
        mvc.perform(post("/api/anotaciones").header("Authorization", bearer("RESPONSABLE"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"zonaId\":1,\"texto\":\"ok\"}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.codigo").value("VALIDACION"))
            .andExpect(jsonPath("$.errores[0].campo").value("texto"));

        mvc.perform(post("/api/anotaciones").header("Authorization", bearer("RESPONSABLE"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"zonaId\":\"abc\",\"texto\":\"Riego manual.\"}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.codigo").value("VALIDACION"));
    }

    @Test
    @DisplayName("404 y 422 segun lo que reporte el servicio")
    void erroresDelServicio() throws Exception {
        when(servicio.porId(999L)).thenThrow(ApiException.noEncontrado("La anotacion 999 no existe."));
        mvc.perform(get("/api/anotaciones/999").header("Authorization", bearer("COORDINACION")))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.mensaje").value("La anotacion 999 no existe."));

        when(servicio.registrar(any(), any())).thenThrow(ApiException.noEncontrado("La zona 999 no existe."));
        mvc.perform(post("/api/anotaciones").header("Authorization", bearer("RESPONSABLE"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"zonaId\":999,\"texto\":\"Riego manual.\"}"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.codigo").value("NO_ENCONTRADO"));

        org.mockito.Mockito.reset(servicio);
        when(servicio.registrar(any(), any()))
            .thenThrow(ApiException.reglaDeNegocio("La lectura 12 pertenece a Cama A, no a Invernadero 1."));
        mvc.perform(post("/api/anotaciones").header("Authorization", bearer("RESPONSABLE"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"zonaId\":2,\"lecturaId\":12,\"texto\":\"Riego manual.\"}"))
            .andExpect(status().isUnprocessableEntity())
            .andExpect(jsonPath("$.codigo").value("REGLA_DE_NEGOCIO"));
    }
}
