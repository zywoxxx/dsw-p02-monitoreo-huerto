package mx.uv.dsw.huerto.api.lecturas;

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

import mx.uv.dsw.huerto.api.seguridad.Permisos.Permiso;
import mx.uv.dsw.huerto.api.seguridad.UsuarioAutenticado;

/**
 * Recurso /api/lecturas (RF03, RF05). El controlador solo traduce HTTP; las reglas estan en
 * LecturaService y ReglasLectura, y el SQL en LecturaRepository.
 */
@RestController
@RequestMapping("/api/lecturas")
public class LecturaController {

    private final LecturaService servicio;

    public LecturaController(LecturaService servicio) {
        this.servicio = servicio;
    }

    @GetMapping
    public Pagina<Lectura> listar(@RequestParam(required = false) Long sensorId,
                                  @RequestParam(required = false) Long zonaId,
                                  @RequestParam(required = false) String origen,
                                  @RequestParam(defaultValue = "0") int pagina,
                                  @RequestParam(defaultValue = "10") int tamano,
                                  HttpServletRequest request) {
        UsuarioAutenticado.de(request).exigir(Permiso.CONSULTAR);
        return servicio.listar(sensorId, zonaId, origen, pagina, tamano);
    }

    @GetMapping("/{id}")
    public Lectura porId(@PathVariable long id, HttpServletRequest request) {
        UsuarioAutenticado.de(request).exigir(Permiso.CONSULTAR);
        return servicio.porId(id);
    }

    @PostMapping
    public ResponseEntity<Lectura> registrar(@RequestBody LecturaRequest peticion, HttpServletRequest request) {
        UsuarioAutenticado.de(request).exigir(Permiso.REGISTRAR_LECTURA);
        Lectura creada = servicio.registrar(peticion);
        return ResponseEntity.created(URI.create("/api/lecturas/" + creada.getId())).body(creada);
    }
}
