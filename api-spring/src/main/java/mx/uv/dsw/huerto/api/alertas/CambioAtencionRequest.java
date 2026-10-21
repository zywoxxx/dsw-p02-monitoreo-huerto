package mx.uv.dsw.huerto.api.alertas;

/**
 * Cuerpo de PATCH /api/alertas/{id}. "atendida" se recibe como Boolean (no boolean) para distinguir
 * un campo ausente de false y rechazarlo con 400. El rol y el instante de atencion no viajan en el
 * cuerpo: los pone el servidor.
 */
public class CambioAtencionRequest {

    private Boolean atendida;

    public Boolean getAtendida() {
        return atendida;
    }

    public void setAtendida(Boolean atendida) {
        this.atendida = atendida;
    }
}
