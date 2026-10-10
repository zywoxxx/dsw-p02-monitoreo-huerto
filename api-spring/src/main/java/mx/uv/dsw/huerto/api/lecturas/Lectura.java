package mx.uv.dsw.huerto.api.lecturas;

import java.math.BigDecimal;
import java.time.OffsetDateTime;

/** Lectura con los datos del sensor y, si existe, su alerta (esquema "Lectura" del contrato). */
public class Lectura {

    /** Alerta asociada a la lectura. */
    public static class AlertaResumen {
        private final String nivel;
        private final String mensaje;

        public AlertaResumen(String nivel, String mensaje) {
            this.nivel = nivel;
            this.mensaje = mensaje;
        }

        public String getNivel() {
            return nivel;
        }

        public String getMensaje() {
            return mensaje;
        }
    }

    private long id;
    private long sensorId;
    private String sensorCodigo;
    private String variable;
    private String zona;
    private BigDecimal valor;
    private String unidad;
    private String origen;
    private String observacion;
    private OffsetDateTime registradoEn;
    private AlertaResumen alerta;

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public long getSensorId() {
        return sensorId;
    }

    public void setSensorId(long sensorId) {
        this.sensorId = sensorId;
    }

    public String getSensorCodigo() {
        return sensorCodigo;
    }

    public void setSensorCodigo(String sensorCodigo) {
        this.sensorCodigo = sensorCodigo;
    }

    public String getVariable() {
        return variable;
    }

    public void setVariable(String variable) {
        this.variable = variable;
    }

    public String getZona() {
        return zona;
    }

    public void setZona(String zona) {
        this.zona = zona;
    }

    public BigDecimal getValor() {
        return valor;
    }

    public void setValor(BigDecimal valor) {
        this.valor = valor;
    }

    public String getUnidad() {
        return unidad;
    }

    public void setUnidad(String unidad) {
        this.unidad = unidad;
    }

    public String getOrigen() {
        return origen;
    }

    public void setOrigen(String origen) {
        this.origen = origen;
    }

    public String getObservacion() {
        return observacion;
    }

    public void setObservacion(String observacion) {
        this.observacion = observacion;
    }

    public OffsetDateTime getRegistradoEn() {
        return registradoEn;
    }

    public void setRegistradoEn(OffsetDateTime registradoEn) {
        this.registradoEn = registradoEn;
    }

    public AlertaResumen getAlerta() {
        return alerta;
    }

    public void setAlerta(AlertaResumen alerta) {
        this.alerta = alerta;
    }
}
