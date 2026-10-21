package mx.uv.dsw.huerto.api.zonas;

import java.util.List;

import javax.servlet.http.HttpServletRequest;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import mx.uv.dsw.huerto.api.seguridad.Permisos.Permiso;
import mx.uv.dsw.huerto.api.seguridad.UsuarioAutenticado;

/** GET /api/zonas : catalogo para los selectores y filtros del cliente (RF01). */
@RestController
public class ZonaController {

    private final ZonaRepository zonas;

    public ZonaController(ZonaRepository zonas) {
        this.zonas = zonas;
    }

    @GetMapping("/api/zonas")
    public List<Zona> listar(HttpServletRequest request) {
        UsuarioAutenticado.de(request).exigir(Permiso.CONSULTAR);
        return zonas.listar();
    }
}
