package mx.uv.dsw.huerto.api.alertas;

import java.math.BigDecimal;
import java.time.OffsetDateTime;

/**
 * Alerta con los datos de la lectura y el sensor que la generaron, mas su atencion (esquema "Alerta"
 * del contrato). atendidaEn y atendidaPor solo tienen valor cuando atendida es true.
 */
public class Alerta {

    private long id;
    private long lecturaId;
    private String sensorCodigo;
    private String variable;
    private long zonaId;
    private String zona;
    private BigDecimal valor;
    private String unidad;
    private String nivel;
    private String mensaje;
    private boolean atendida;
    private OffsetDateTime atendidaEn;
    private String atendidaPor;
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

    public String getVariable() {
        return variable;
    }

    public void setVariable(String variable) {
        this.variable = variable;
    }

    public long getZonaId() {
        return zonaId;
    }

    public void setZonaId(long zonaId) {
        this.zonaId = zonaId;
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

    public OffsetDateTime getAtendidaEn() {
        return atendidaEn;
    }

    public void setAtendidaEn(OffsetDateTime atendidaEn) {
        this.atendidaEn = atendidaEn;
    }

    public String getAtendidaPor() {
        return atendidaPor;
    }

    public void setAtendidaPor(String atendidaPor) {
        this.atendidaPor = atendidaPor;
    }

    public OffsetDateTime getCreadaEn() {
        return creadaEn;
    }

    public void setCreadaEn(OffsetDateTime creadaEn) {
        this.creadaEn = creadaEn;
    }
}
