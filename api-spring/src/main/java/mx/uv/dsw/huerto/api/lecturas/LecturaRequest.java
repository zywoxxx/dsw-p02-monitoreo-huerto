package mx.uv.dsw.huerto.api.lecturas;

import java.math.BigDecimal;

/**
 * Cuerpo de POST /api/lecturas. "valor" se recibe como BigDecimal: Jackson conserva los decimales tal
 * como llegan (24.555 sigue teniendo tres), asi la regla de maximo dos decimales se puede rechazar
 * en lugar de redondear. El origen no se acepta del cliente: una captura por API es "manual".
 */
public class LecturaRequest {

    private Long sensorId;
    private BigDecimal valor;
    private String observacion;

    public Long getSensorId() {
        return sensorId;
    }

    public void setSensorId(Long sensorId) {
        this.sensorId = sensorId;
    }

    public BigDecimal getValor() {
        return valor;
    }

    public void setValor(BigDecimal valor) {
        this.valor = valor;
    }

    public String getObservacion() {
        return observacion;
    }

    public void setObservacion(String observacion) {
        this.observacion = observacion;
    }
}
