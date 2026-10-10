package mx.uv.dsw.huerto.api.lecturas;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import mx.uv.dsw.huerto.api.error.ApiError;
import mx.uv.dsw.huerto.api.error.ApiException;
import mx.uv.dsw.huerto.api.sensores.Sensor;
import mx.uv.dsw.huerto.api.sensores.SensorRepository;

/**
 * Flujo principal del PR09 como servicio: validar, persistir y generar la alerta en una transaccion.
 * Cada salida anomala corresponde a un estado HTTP del contrato (400, 404, 409, 422).
 */
@Service
public class LecturaService {

    private static final int TAMANO_MAXIMO = 100;

    private final SensorRepository sensores;
    private final LecturaRepository lecturas;

    public LecturaService(SensorRepository sensores, LecturaRepository lecturas) {
        this.sensores = sensores;
        this.lecturas = lecturas;
    }

    @Transactional(readOnly = true)
    public Pagina<Lectura> listar(Long sensorId, Long zonaId, String origen, int pagina, int tamano) {
        if (pagina < 0 || tamano < 1 || tamano > TAMANO_MAXIMO) {
            throw ApiException.validacion(List.of(new ApiError.Campo("pagina/tamano",
                "pagina debe ser >= 0 y tamano estar entre 1 y " + TAMANO_MAXIMO + ".")));
        }
        if (origen != null && !origen.equals("manual") && !origen.equals("simulado")) {
            throw ApiException.validacion(List.of(new ApiError.Campo("origen", "origen debe ser manual o simulado.")));
        }
        return new Pagina<>(lecturas.buscar(sensorId, zonaId, origen, tamano, pagina * tamano),
            pagina, tamano, lecturas.contar(sensorId, zonaId, origen));
    }

    @Transactional(readOnly = true)
    public Lectura porId(long id) {
        return lecturas.porId(id).orElseThrow(() -> ApiException.noEncontrado("La lectura " + id + " no existe."));
    }

    /** Lectura + alerta en la misma transaccion: si la alerta falla, la lectura tampoco queda. */
    @Transactional
    public Lectura registrar(LecturaRequest peticion) {
        List<ApiError.Campo> errores = ReglasLectura.validarForma(peticion);
        if (!errores.isEmpty()) {
            throw ApiException.validacion(errores);
        }
        Sensor sensor = sensores.porId(peticion.getSensorId())
            .orElseThrow(() -> ApiException.noEncontrado("El sensor " + peticion.getSensorId() + " no existe."));
        if (!sensor.isActivo()) {
            throw ApiException.conflicto("El sensor " + sensor.getCodigo() + " esta inactivo; no admite lecturas.");
        }
        if (!ReglasLectura.dentroDelRangoFisico(sensor, peticion.getValor())) {
            throw ApiException.reglaDeNegocio("El valor " + peticion.getValor().toPlainString() + " " + sensor.getUnidad()
                + " esta fuera del rango fisico de " + sensor.getVariable() + " ["
                + sensor.getRangoFisicoMinimo().toPlainString() + ", " + sensor.getRangoFisicoMaximo().toPlainString() + "].");
        }
        String observacion = peticion.getObservacion() == null || peticion.getObservacion().isBlank()
            ? null : peticion.getObservacion().trim();
        long id = lecturas.insertarLectura(sensor.getId(), peticion.getValor(), observacion);
        String nivel = ReglasLectura.nivelAlerta(sensor, peticion.getValor());
        if (nivel != null) {
            lecturas.insertarAlerta(id, nivel, ReglasLectura.mensajeAlerta(sensor, peticion.getValor(), nivel));
        }
        return porId(id);
    }
}
