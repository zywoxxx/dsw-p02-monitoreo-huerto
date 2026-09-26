package mx.uv.dsw.huerto.web;

import javax.faces.application.FacesMessage;
import javax.faces.context.FacesContext;

/** Atajos para agregar mensajes globales a la vista JSF. */
final class Mensajes {

    private Mensajes() {
    }

    static void info(String resumen, String detalle) {
        agregar(FacesMessage.SEVERITY_INFO, resumen, detalle);
    }

    static void advertencia(String resumen, String detalle) {
        agregar(FacesMessage.SEVERITY_WARN, resumen, detalle);
    }

    static void error(String resumen, String detalle) {
        agregar(FacesMessage.SEVERITY_ERROR, resumen, detalle);
    }

    private static void agregar(FacesMessage.Severity severidad, String resumen, String detalle) {
        FacesContext fc = FacesContext.getCurrentInstance();
        if (fc != null) {
            fc.addMessage(null, new FacesMessage(severidad, resumen, detalle));
        }
    }
}
