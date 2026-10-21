package mx.uv.dsw.huerto.api.alertas;

import javax.servlet.http.HttpServletRequest;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import mx.uv.dsw.huerto.api.lecturas.Pagina;
import mx.uv.dsw.huerto.api.seguridad.Permisos.Permiso;
import mx.uv.dsw.huerto.api.seguridad.UsuarioAutenticado;

/**
 * Recurso /api/alertas (RF06). El controlador solo traduce HTTP; las reglas estan en AlertaService y
 * el SQL en AlertaRepository. Consultar es de cualquier rol; atender o reabrir solo del RESPONSABLE.
 */
@RestController
@RequestMapping("/api/alertas")
public class AlertaController {

    private final AlertaService servicio;

    public AlertaController(AlertaService servicio) {
        this.servicio = servicio;
    }

    @GetMapping
    public Pagina<Alerta> listar(@RequestParam(required = false) String nivel,
                                 @RequestParam(required = false) Boolean atendida,
                                 @RequestParam(required = false) Long zonaId,
                                 @RequestParam(defaultValue = "0") int pagina,
                                 @RequestParam(defaultValue = "10") int tamano,
                                 HttpServletRequest request) {
        UsuarioAutenticado.de(request).exigir(Permiso.CONSULTAR);
        return servicio.listar(nivel, atendida, zonaId, pagina, tamano);
    }

    @GetMapping("/{id}")
    public Alerta porId(@PathVariable long id, HttpServletRequest request) {
        UsuarioAutenticado.de(request).exigir(Permiso.CONSULTAR);
        return servicio.porId(id);
    }

    @PatchMapping("/{id}")
    public Alerta cambiarAtencion(@PathVariable long id, @RequestBody CambioAtencionRequest peticion,
                                  HttpServletRequest request) {
        UsuarioAutenticado usuario = UsuarioAutenticado.de(request);
        usuario.exigir(Permiso.ATENDER_ALERTA);
        return servicio.cambiarAtencion(id, peticion.getAtendida(), usuario.getRol());
    }
}
