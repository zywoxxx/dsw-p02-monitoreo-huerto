package mx.uv.dsw.huerto.api.anotaciones;

import java.time.OffsetDateTime;

/** Anotacion de un rol sobre una zona y, si la refiere, una lectura (esquema "Anotacion" del contrato). */
public class Anotacion {

    private long id;
    private long zonaId;
    private String zona;
    private Long lecturaId;
    private String autorRol;
    private String texto;
    private OffsetDateTime creadaEn;

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
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

    public Long getLecturaId() {
        return lecturaId;
    }

    public void setLecturaId(Long lecturaId) {
        this.lecturaId = lecturaId;
    }

    public String getAutorRol() {
        return autorRol;
    }

    public void setAutorRol(String autorRol) {
        this.autorRol = autorRol;
    }

    public String getTexto() {
        return texto;
    }

    public void setTexto(String texto) {
        this.texto = texto;
    }

    public OffsetDateTime getCreadaEn() {
        return creadaEn;
    }

    public void setCreadaEn(OffsetDateTime creadaEn) {
        this.creadaEn = creadaEn;
    }
}
