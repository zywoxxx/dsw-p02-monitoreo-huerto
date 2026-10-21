package mx.uv.dsw.huerto.api.alertas;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import mx.uv.dsw.huerto.api.error.ApiError;
import mx.uv.dsw.huerto.api.error.ApiException;
import mx.uv.dsw.huerto.api.lecturas.Pagina;

/**
 * Consulta de alertas y cambio de estado (RF06). Cada salida anomala corresponde a un estado HTTP del
 * contrato: 400 filtros o cuerpo invalidos, 404 no existe, 409 ya estaba en el estado pedido.
 */
@Service
public class AlertaService {

    private static final int TAMANO_MAXIMO = 100;

    private final AlertaRepository alertas;

    public AlertaService(AlertaRepository alertas) {
        this.alertas = alertas;
    }

    @Transactional(readOnly = true)
    public Pagina<Alerta> listar(String nivel, Boolean atendida, Long zonaId, int pagina, int tamano) {
        if (pagina < 0 || tamano < 1 || tamano > TAMANO_MAXIMO) {
            throw ApiException.validacion(List.of(new ApiError.Campo("pagina/tamano",
                "pagina debe ser >= 0 y tamano estar entre 1 y " + TAMANO_MAXIMO + ".")));
        }
        if (nivel != null && !nivel.equals("BAJA") && !nivel.equals("ALTA")) {
            throw ApiException.validacion(List.of(new ApiError.Campo("nivel", "nivel debe ser BAJA o ALTA.")));
        }
        return new Pagina<>(alertas.buscar(nivel, atendida, zonaId, tamano, pagina * tamano),
            pagina, tamano, alertas.contar(nivel, atendida, zonaId));
    }

    @Transactional(readOnly = true)
    public Alerta porId(long id) {
        return alertas.porId(id).orElseThrow(() -> ApiException.noEncontrado("La alerta " + id + " no existe."));
    }

    /**
     * Atiende (true) o reabre (false) la alerta; el rol es el del token, nunca del cuerpo. El UPDATE
     * exige el estado contrario al pedido, asi que si dos peticiones llegan a la vez solo una cambia
     * el estado y la otra recibe 409, igual que si lo hubiera pedido despues.
     */
    @Transactional
    public Alerta cambiarAtencion(long id, Boolean atendida, String rol) {
        if (atendida == null) {
            throw ApiException.validacion(List.of(new ApiError.Campo("atendida", "Indica atendida: true o false.")));
        }
        Alerta actual = porId(id);
        if (actual.isAtendida() == atendida || alertas.actualizarAtencion(id, atendida, rol) == 0) {
            throw ApiException.conflicto("La alerta " + id + " ya estaba " + (atendida ? "atendida." : "pendiente."));
        }
        return porId(id);
    }
}
