package mx.uv.dsw.huerto.api.lecturas;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.math.BigDecimal;
import java.util.List;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.dao.DataAccessResourceFailureException;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.CannotCreateTransactionException;

import mx.uv.dsw.huerto.api.error.ApiError;
import mx.uv.dsw.huerto.api.error.ApiException;
import mx.uv.dsw.huerto.api.error.ApiExceptionHandler;
import mx.uv.dsw.huerto.api.seguridad.TokenFilter;
import mx.uv.dsw.huerto.api.seguridad.TokenService;

/**
 * Contrato HTTP de /api/lecturas sin base de datos: el servicio se simula y se comprueba que cada
 * situacion responde con el estado y el cuerpo que promete openapi.yaml.
 */
@WebMvcTest(LecturaController.class)
@Import({TokenService.class, TokenFilter.class, ApiExceptionHandler.class})
@TestPropertySource(properties = {"huerto.jwt.secreto=secreto-de-prueba-de-32-caracteres-o-mas", "huerto.jwt.minutos=30",
    "huerto.cors.origen=http://localhost:4200"})
class LecturaControllerTest {

    @Autowired
    private MockMvc mvc;

    @Autowired
    private TokenService tokens;

    @MockBean
    private LecturaService servicio;

    private String bearer(String rol) {
        return "Bearer " + tokens.emitir(rol.toLowerCase(), rol);
    }

    private static Lectura lectura(long id, String valor, String nivel) {
        Lectura l = new Lectura();
        l.setId(id);
        l.setSensorId(2);
        l.setSensorCodigo("SEN-A-TEMP-01");
        l.setValor(new BigDecimal(valor));
        l.setUnidad("C");
        l.setOrigen("manual");
        if (nivel != null) {
            l.setAlerta(new Lectura.AlertaResumen(nivel, "mensaje"));
        }
        return l;
    }

    @Test
    @DisplayName("401 sin token y con token invalido")
    void sinToken() throws Exception {
        mvc.perform(get("/api/lecturas")).andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.codigo").value("NO_AUTENTICADO"));
        mvc.perform(get("/api/lecturas").header("Authorization", "Bearer abc.def.ghi"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("200 GET con cualquier rol")
    void listar() throws Exception {
        when(servicio.listar(any(), any(), any(), any(Integer.class), any(Integer.class)))
            .thenReturn(new Pagina<>(List.of(lectura(1, "24.50", null)), 0, 10, 1));
        mvc.perform(get("/api/lecturas").header("Authorization", bearer("COORDINACION")))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.total").value(1))
            .andExpect(jsonPath("$.contenido[0].sensorCodigo").value("SEN-A-TEMP-01"));
    }

    @Test
    @DisplayName("201 POST valido del observador, con Location y alerta")
    void crear() throws Exception {
        when(servicio.registrar(any())).thenReturn(lectura(9, "38", "ALTA"));
        mvc.perform(post("/api/lecturas").header("Authorization", bearer("OBSERVADOR"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"sensorId\":2,\"valor\":38}"))
            .andExpect(status().isCreated())
            .andExpect(header().string("Location", "/api/lecturas/9"))
            .andExpect(jsonPath("$.alerta.nivel").value("ALTA"))
            .andExpect(jsonPath("$.origen").value("manual"));
    }

    @Test
    @DisplayName("403 POST con un rol sin permiso")
    void rolSinPermiso() throws Exception {
        mvc.perform(post("/api/lecturas").header("Authorization", bearer("COORDINACION"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"sensorId\":2,\"valor\":25.5}"))
            .andExpect(status().isForbidden())
            .andExpect(jsonPath("$.codigo").value("ROL_SIN_PERMISO"));
    }

    @Test
    @DisplayName("400 cuando valor no es numerico o el JSON esta mal formado")
    void noNumerico() throws Exception {
        mvc.perform(post("/api/lecturas").header("Authorization", bearer("OBSERVADOR"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"sensorId\":2,\"valor\":\"abc\"}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.codigo").value("VALIDACION"));
    }

    @Test
    @DisplayName("400, 404, 409 y 422 segun lo que reporte el servicio")
    void erroresDelServicio() throws Exception {
        String cuerpo = "{\"sensorId\":2,\"valor\":24.555}";
        when(servicio.registrar(any())).thenThrow(ApiException.validacion(List.of(new ApiError.Campo("valor", "decimales"))));
        mvc.perform(post("/api/lecturas").header("Authorization", bearer("OBSERVADOR"))
                .contentType(MediaType.APPLICATION_JSON).content(cuerpo))
            .andExpect(status().isBadRequest()).andExpect(jsonPath("$.errores[0].campo").value("valor"));

        org.mockito.Mockito.reset(servicio);
        when(servicio.registrar(any())).thenThrow(ApiException.noEncontrado("El sensor 999 no existe."));
        mvc.perform(post("/api/lecturas").header("Authorization", bearer("OBSERVADOR"))
                .contentType(MediaType.APPLICATION_JSON).content(cuerpo))
            .andExpect(status().isNotFound());

        org.mockito.Mockito.reset(servicio);
        when(servicio.registrar(any())).thenThrow(ApiException.conflicto("inactivo"));
        mvc.perform(post("/api/lecturas").header("Authorization", bearer("OBSERVADOR"))
                .contentType(MediaType.APPLICATION_JSON).content(cuerpo))
            .andExpect(status().isConflict());

        org.mockito.Mockito.reset(servicio);
        when(servicio.registrar(any())).thenThrow(ApiException.reglaDeNegocio("fuera del rango fisico"));
        mvc.perform(post("/api/lecturas").header("Authorization", bearer("OBSERVADOR"))
                .contentType(MediaType.APPLICATION_JSON).content(cuerpo))
            .andExpect(status().isUnprocessableEntity())
            .andExpect(jsonPath("$.codigo").value("REGLA_DE_NEGOCIO"));
    }

    @Test
    @DisplayName("503 si la base no responde, tanto al consultar como al abrir la transaccion")
    void baseNoDisponible() throws Exception {
        when(servicio.registrar(any()))
            .thenThrow(new CannotCreateTransactionException("sin conexion"));
        mvc.perform(post("/api/lecturas").header("Authorization", bearer("OBSERVADOR"))
                .contentType(MediaType.APPLICATION_JSON).content("{\"sensorId\":2,\"valor\":25.5}"))
            .andExpect(status().isServiceUnavailable())
            .andExpect(jsonPath("$.codigo").value("BASE_NO_DISPONIBLE"));

        when(servicio.porId(1L)).thenThrow(new DataAccessResourceFailureException("sin conexion"));
        mvc.perform(get("/api/lecturas/1").header("Authorization", bearer("OBSERVADOR")))
            .andExpect(status().isServiceUnavailable())
            .andExpect(jsonPath("$.codigo").value("BASE_NO_DISPONIBLE"));
    }
}
