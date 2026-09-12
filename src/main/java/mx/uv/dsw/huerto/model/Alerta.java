package mx.uv.dsw.huerto.model;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;

/** Alerta generada automaticamente por una lectura fuera del umbral (RF06). */
public class Alerta {

    private long id;
    private long lecturaId;
    private String sensorCodigo;
    private String zona;
    private BigDecimal valor;
    private String unidad;
    private String nivel;
    private String mensaje;
    private boolean atendida;
    private OffsetDateTime creadaEn;

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public long getLecturaId() {
        return lecturaId;
    }

    public void setLecturaId(long lecturaId) {
        this.lecturaId = lecturaId;
    }

    public String getSensorCodigo() {
        return sensorCodigo;
    }

    public void setSensorCodigo(String sensorCodigo) {
        this.sensorCodigo = sensorCodigo;
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

    public String getNivel() {
        return nivel;
    }

    public void setNivel(String nivel) {
        this.nivel = nivel;
    }

    public String getMensaje() {
        return mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }

    public boolean isAtendida() {
        return atendida;
    }

    public void setAtendida(boolean atendida) {
        this.atendida = atendida;
    }

    public OffsetDateTime getCreadaEn() {
        return creadaEn;
    }

    public void setCreadaEn(OffsetDateTime creadaEn) {
        this.creadaEn = creadaEn;
    }

    /** Fecha formateada para la vista (JSTL fmt no acepta java.time). */
    public String getCreadaEnTexto() {
        return creadaEn == null ? "" : creadaEn.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }
}
