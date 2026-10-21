package mx.uv.dsw.huerto.api.anotaciones;

import java.net.URI;

import javax.servlet.http.HttpServletRequest;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import mx.uv.dsw.huerto.api.lecturas.Pagina;
import mx.uv.dsw.huerto.api.seguridad.Permisos.Permiso;
import mx.uv.dsw.huerto.api.seguridad.UsuarioAutenticado;

/**
 * Recurso /api/anotaciones (RF06). El controlador solo traduce HTTP; las reglas estan en
 * AnotacionService y ReglasAnotacion, y el SQL en AnotacionRepository.
 */
@RestController
@RequestMapping("/api/anotaciones")
public class AnotacionController {

    private final AnotacionService servicio;

    public AnotacionController(AnotacionService servicio) {
        this.servicio = servicio;
    }

    @GetMapping
    public Pagina<Anotacion> listar(@RequestParam(required = false) Long zonaId,
                                    @RequestParam(defaultValue = "0") int pagina,
                                    @RequestParam(defaultValue = "10") int tamano,
                                    HttpServletRequest request) {
        UsuarioAutenticado.de(request).exigir(Permiso.CONSULTAR);
        return servicio.listar(zonaId, pagina, tamano);
    }

    @GetMapping("/{id}")
    public Anotacion porId(@PathVariable long id, HttpServletRequest request) {
        UsuarioAutenticado.de(request).exigir(Permiso.CONSULTAR);
        return servicio.porId(id);
    }

    @PostMapping
    public ResponseEntity<Anotacion> registrar(@RequestBody AnotacionRequest peticion, HttpServletRequest request) {
        UsuarioAutenticado usuario = UsuarioAutenticado.de(request);
        usuario.exigir(Permiso.ANOTAR);
        Anotacion creada = servicio.registrar(peticion, usuario.getRol());
        return ResponseEntity.created(URI.create("/api/anotaciones/" + creada.getId())).body(creada);
    }
}
