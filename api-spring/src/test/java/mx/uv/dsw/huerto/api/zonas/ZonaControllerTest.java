package mx.uv.dsw.huerto.api.zonas;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import mx.uv.dsw.huerto.api.error.ApiExceptionHandler;
import mx.uv.dsw.huerto.api.seguridad.TokenFilter;
import mx.uv.dsw.huerto.api.seguridad.TokenService;

/** Contrato HTTP de /api/zonas sin base de datos: exige token y devuelve la lista del repositorio. */
@WebMvcTest(ZonaController.class)
@Import({TokenService.class, TokenFilter.class, ApiExceptionHandler.class})
@TestPropertySource(properties = {"huerto.jwt.secreto=secreto-de-prueba-de-32-caracteres-o-mas", "huerto.jwt.minutos=30",
    "huerto.cors.origen=http://localhost:4200"})
class ZonaControllerTest {

    @Autowired
    private MockMvc mvc;

    @Autowired
    private TokenService tokens;

    @MockBean
    private ZonaRepository zonas;

    private static Zona zona(long id, String nombre, String cultivo) {
        Zona z = new Zona();
        z.setId(id);
        z.setNombre(nombre);
        z.setCultivo(cultivo);
        z.setUbicacion("Huerto escolar demo (ficticio)");
        return z;
    }

    @Test
    @DisplayName("401 sin token")
    void sinToken() throws Exception {
        mvc.perform(get("/api/zonas")).andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.codigo").value("NO_AUTENTICADO"));
    }

    @Test
    @DisplayName("200 con cualquier rol: lista con id, nombre, cultivo y ubicacion")
    void listar() throws Exception {
        when(zonas.listar()).thenReturn(List.of(zona(1, "Cama A", "Jitomate"), zona(2, "Invernadero 1", "Lechuga")));
        mvc.perform(get("/api/zonas").header("Authorization", "Bearer " + tokens.emitir("responsable", "RESPONSABLE")))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.length()").value(2))
            .andExpect(jsonPath("$[0].id").value(1))
            .andExpect(jsonPath("$[0].nombre").value("Cama A"))
            .andExpect(jsonPath("$[1].nombre").value("Invernadero 1"))
            .andExpect(jsonPath("$[1].ubicacion").exists());
    }
}
