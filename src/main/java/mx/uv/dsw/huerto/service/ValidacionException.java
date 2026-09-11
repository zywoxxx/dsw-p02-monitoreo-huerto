package mx.uv.dsw.huerto.service;

import java.util.Collections;
import java.util.List;

/** Se lanza cuando la entrada del usuario no cumple las reglas de RF-03; contiene todos los errores. */
public class ValidacionException extends Exception {

    private static final long serialVersionUID = 1L;

    private final List<String> errores;

    public ValidacionException(List<String> errores) {
        super(String.join("; ", errores));
        this.errores = Collections.unmodifiableList(errores);
    }

    public List<String> getErrores() {
        return errores;
    }
}
