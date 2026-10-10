package mx.uv.dsw.huerto.api.sensores;

import java.math.BigDecimal;

/** Sensor con su zona, variable, rango fisico y umbral operativo (esquema "Sensor" del contrato). */
public class Sensor {

    private long id;
    private String codigo;
    private boolean activo;
    private long zonaId;
    private String zona;
    private String variable;
    private String unidad;
    private BigDecimal rangoFisicoMinimo;
    private BigDecimal rangoFisicoMaximo;
    private BigDecimal umbralMinimo;
    private BigDecimal umbralMaximo;

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public String getCodigo() {
        return codigo;
    }

    public void setCodigo(String codigo) {
        this.codigo = codigo;
    }

    public boolean isActivo() {
        return activo;
    }

    public void setActivo(boolean activo) {
        this.activo = activo;
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

    public String getVariable() {
        return variable;
    }

    public void setVariable(String variable) {
        this.variable = variable;
    }

    public String getUnidad() {
        return unidad;
    }

    public void setUnidad(String unidad) {
        this.unidad = unidad;
    }

    public BigDecimal getRangoFisicoMinimo() {
        return rangoFisicoMinimo;
    }

    public void setRangoFisicoMinimo(BigDecimal rangoFisicoMinimo) {
        this.rangoFisicoMinimo = rangoFisicoMinimo;
    }

    public BigDecimal getRangoFisicoMaximo() {
        return rangoFisicoMaximo;
    }

    public void setRangoFisicoMaximo(BigDecimal rangoFisicoMaximo) {
        this.rangoFisicoMaximo = rangoFisicoMaximo;
    }

    public BigDecimal getUmbralMinimo() {
        return umbralMinimo;
    }

    public void setUmbralMinimo(BigDecimal umbralMinimo) {
        this.umbralMinimo = umbralMinimo;
    }

    public BigDecimal getUmbralMaximo() {
        return umbralMaximo;
    }

    public void setUmbralMaximo(BigDecimal umbralMaximo) {
        this.umbralMaximo = umbralMaximo;
    }
}
