package mx.uv.dsw.huerto.model;

import java.math.BigDecimal;

/**
 * Sensor instalado en una zona, con los datos de su variable (RF02) y umbral (RF04)
 * necesarios para validar y clasificar una lectura (RF03, RF06).
 */
public class Sensor {

    private long id;
    private String codigo;
    private boolean activo;
    private long zonaId;
    private String zona;
    private String variableClave;
    private String variableNombre;
    private String unidad;
    /** Rango fisico valido de la variable (tabla variable). */
    private BigDecimal valorMinimo;
    private BigDecimal valorMaximo;
    /** Rango operativo deseado (tabla umbral); puede ser nulo si no hay umbral. */
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

    public String getVariableClave() {
        return variableClave;
    }

    public void setVariableClave(String variableClave) {
        this.variableClave = variableClave;
    }

    public String getVariableNombre() {
        return variableNombre;
    }

    public void setVariableNombre(String variableNombre) {
        this.variableNombre = variableNombre;
    }

    public String getUnidad() {
        return unidad;
    }

    public void setUnidad(String unidad) {
        this.unidad = unidad;
    }

    public BigDecimal getValorMinimo() {
        return valorMinimo;
    }

    public void setValorMinimo(BigDecimal valorMinimo) {
        this.valorMinimo = valorMinimo;
    }

    public BigDecimal getValorMaximo() {
        return valorMaximo;
    }

    public void setValorMaximo(BigDecimal valorMaximo) {
        this.valorMaximo = valorMaximo;
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

    public boolean isConUmbral() {
        return umbralMinimo != null && umbralMaximo != null;
    }

    /** Etiqueta legible para el selector del formulario. */
    public String getEtiqueta() {
        return codigo + " - " + variableNombre + " (" + unidad + ") - " + zona;
    }
}
