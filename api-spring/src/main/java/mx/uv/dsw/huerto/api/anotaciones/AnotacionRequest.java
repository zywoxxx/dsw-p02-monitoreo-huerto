package mx.uv.dsw.huerto.api.anotaciones;

/**
 * Cuerpo de POST /api/anotaciones. Los identificadores se reciben como Long para distinguir un campo
 * ausente de cero. El rol del autor no se acepta del cliente: se toma del token.
 */
public class AnotacionRequest {

    private Long zonaId;
    private Long lecturaId;
    private String texto;

    public Long getZonaId() {
        return zonaId;
    }

    public void setZonaId(Long zonaId) {
        this.zonaId = zonaId;
    }

    public Long getLecturaId() {
        return lecturaId;
    }

    public void setLecturaId(Long lecturaId) {
        this.lecturaId = lecturaId;
    }

    public String getTexto() {
        return texto;
    }

    public void setTexto(String texto) {
        this.texto = texto;
    }
}
