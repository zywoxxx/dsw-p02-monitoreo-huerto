package mx.uv.dsw.huerto.api.anotaciones;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import mx.uv.dsw.huerto.api.error.ApiError;
import mx.uv.dsw.huerto.api.error.ApiException;
import mx.uv.dsw.huerto.api.lecturas.Pagina;
import mx.uv.dsw.huerto.api.zonas.Zona;
import mx.uv.dsw.huerto.api.zonas.ZonaRepository;

/**
 * Consulta y registro de anotaciones (RF06). Cada salida anomala corresponde a un estado HTTP del
 * contrato: 400 forma, 404 zona o lectura inexistente, 422 lectura de otra zona.
 */
@Service
public class AnotacionService {

    private static final int TAMANO_MAXIMO = 100;

    private final ZonaRepository zonas;
    private final AnotacionRepository anotaciones;

    public AnotacionService(ZonaRepository zonas, AnotacionRepository anotaciones) {
        this.zonas = zonas;
        this.anotaciones = anotaciones;
    }

    @Transactional(readOnly = true)
    public Pagina<Anotacion> listar(Long zonaId, int pagina, int tamano) {
        if (pagina < 0 || tamano < 1 || tamano > TAMANO_MAXIMO) {
            throw ApiException.validacion(List.of(new ApiError.Campo("pagina/tamano",
                "pagina debe ser >= 0 y tamano estar entre 1 y " + TAMANO_MAXIMO + ".")));
        }
        return new Pagina<>(anotaciones.buscar(zonaId, tamano, pagina * tamano), pagina, tamano, anotaciones.contar(zonaId));
    }

    @Transactional(readOnly = true)
    public Anotacion porId(long id) {
        return anotaciones.porId(id).orElseThrow(() -> ApiException.noEncontrado("La anotacion " + id + " no existe."));
    }

    /**
     * Valida la forma, comprueba zona y lectura e inserta, todo en una transaccion. El autor es el rol
     * del token, nunca del cuerpo.
     */
    @Transactional
    public Anotacion registrar(AnotacionRequest peticion, String autorRol) {
        List<ApiError.Campo> errores = ReglasAnotacion.validarForma(peticion);
        if (!errores.isEmpty()) {
            throw ApiException.validacion(errores);
        }
        Zona zona = zonas.porId(peticion.getZonaId())
            .orElseThrow(() -> ApiException.noEncontrado("La zona " + peticion.getZonaId() + " no existe."));
        if (peticion.getLecturaId() != null) {
            Zona deLaLectura = zonas.porLectura(peticion.getLecturaId())
                .orElseThrow(() -> ApiException.noEncontrado("La lectura " + peticion.getLecturaId() + " no existe."));
            if (deLaLectura.getId() != zona.getId()) {
                throw ApiException.reglaDeNegocio("La lectura " + peticion.getLecturaId() + " pertenece a "
                    + deLaLectura.getNombre() + ", no a " + zona.getNombre() + ".");
            }
        }
        long id = anotaciones.insertar(zona.getId(), peticion.getLecturaId(), autorRol, peticion.getTexto().trim());
        return porId(id);
    }
}
