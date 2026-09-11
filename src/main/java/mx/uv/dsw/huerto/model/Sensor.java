package mx.uv.dsw.huerto.model;

import java.math.BigDecimal;

/**
 * Sensor instalado en una zona del huerto, con los datos de su tipo y umbral
 * necesarios para validar y clasificar una lectura (RF-01, RF-03, RF-05).
 */
public class Sensor {

    private long id;
    private String codigo;
    private boolean activo;
    private String zona;
    private String huerto;
    private String tipoClave;
    private String tipoNombre;
    private String unidad;
    /** Rango fisico valido de la magnitud (tabla tipo_sensor). */
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

    public String getZona() {
        return zona;
    }

    public void setZona(String zona) {
        this.zona = zona;
    }

    public String getHuerto() {
        return huerto;
    }

    public void setHuerto(String huerto) {
        this.huerto = huerto;
    }

    public String getTipoClave() {
        return tipoClave;
    }

    public void setTipoClave(String tipoClave) {
        this.tipoClave = tipoClave;
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
        return codigo + " - " + tipoNombre + " (" + unidad + ") - " + zona;
    }
}
