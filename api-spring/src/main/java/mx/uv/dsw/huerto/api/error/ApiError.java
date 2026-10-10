package mx.uv.dsw.huerto.api.error;

import java.time.OffsetDateTime;
import java.util.List;

/**
 * Cuerpo unico de error de la API (contrato: esquema "Error" de openapi.yaml).
 * El cliente Angular muestra "mensaje" y, si existen, los errores por campo.
 */
public class ApiError {

    /** Error de un campo concreto de la peticion. */
    public static class Campo {
        private final String campo;
        private final String mensaje;

        public Campo(String campo, String mensaje) {
            this.campo = campo;
            this.mensaje = mensaje;
        }

        public String getCampo() {
            return campo;
        }

        public String getMensaje() {
            return mensaje;
        }
    }

    private final String codigo;
    private final String mensaje;
    private final List<Campo> errores;
    private final OffsetDateTime instante = OffsetDateTime.now();

    public ApiError(String codigo, String mensaje, List<Campo> errores) {
        this.codigo = codigo;
        this.mensaje = mensaje;
        this.errores = errores;
    }

    public ApiError(String codigo, String mensaje) {
        this(codigo, mensaje, null);
    }

    public String getCodigo() {
        return codigo;
    }

    public String getMensaje() {
        return mensaje;
    }

    public List<Campo> getErrores() {
        return errores;
    }

    public OffsetDateTime getInstante() {
        return instante;
    }
}
