package mx.uv.dsw.huerto.model;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Lectura registrada de un sensor (entidad principal del flujo P02, RF-02 y RF-04).
 * Incluye datos desnormalizados del sensor y de la alerta para presentarla en la JSP.
 */
public class Lectura {

    private long id;
    private long sensorId;
    private String sensorCodigo;
    private String tipoNombre;
    private String unidad;
    private String zona;
    private BigDecimal valor;
    private String origen;
    private String observacion;
    private OffsetDateTime registradoEn;
    /** Nivel de la alerta asociada (BAJA/ALTA) o null si la lectura esta en rango. */
    private String alertaNivel;

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

    public String getTipoNombre() {
        return tipoNombre;
    }

    public void setTipoNombre(String tipoNombre) {
        this.tipoNombre = tipoNombre;
    }

    public String getUnidad() {
        return unidad;
    }

    public void setUnidad(String unidad) {
        this.unidad = unidad;
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

    public String getAlertaNivel() {
        return alertaNivel;
    }

    public void setAlertaNivel(String alertaNivel) {
        this.alertaNivel = alertaNivel;
    }

    public boolean isConAlerta() {
        return alertaNivel != null;
    }

    /** Fecha formateada para la vista (JSTL fmt no acepta java.time). */
    public String getRegistradoEnTexto() {
        return registradoEn == null ? "" : registradoEn.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }
}
