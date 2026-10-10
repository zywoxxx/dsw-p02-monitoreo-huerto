package mx.uv.dsw.huerto.api.sensores;

import java.util.List;

import javax.servlet.http.HttpServletRequest;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import mx.uv.dsw.huerto.api.seguridad.Permisos.Permiso;
import mx.uv.dsw.huerto.api.seguridad.UsuarioAutenticado;

/** GET /api/sensores : catalogo para el selector del cliente (RF01, RF02, RF04). */
@RestController
public class SensorController {

    private final SensorRepository sensores;

    public SensorController(SensorRepository sensores) {
        this.sensores = sensores;
    }

    @GetMapping("/api/sensores")
    public List<Sensor> listar(@RequestParam(required = false) Long zonaId,
                               @RequestParam(required = false) Boolean activo,
                               HttpServletRequest request) {
        UsuarioAutenticado.de(request).exigir(Permiso.CONSULTAR);
        return sensores.buscar(zonaId, activo);
    }
}
