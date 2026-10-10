package mx.uv.dsw.huerto.api.error;

import java.util.List;

import org.springframework.http.HttpStatus;

/**
 * Excepcion de la API con su estado HTTP. Un solo tipo con fabricas evita una clase por cada codigo:
 * 400 validacion, 401 sin credenciales, 403 rol sin permiso, 404 no existe, 409 estado, 422 regla de negocio.
 */
public class ApiException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    private final HttpStatus estado;
    private final String codigo;
    private final transient List<ApiError.Campo> errores;

    private ApiException(HttpStatus estado, String codigo, String mensaje, List<ApiError.Campo> errores) {
        super(mensaje);
        this.estado = estado;
        this.codigo = codigo;
        this.errores = errores;
    }

    public static ApiException validacion(List<ApiError.Campo> errores) {
        return new ApiException(HttpStatus.BAD_REQUEST, "VALIDACION",
            "La peticion tiene datos invalidos; no se guardo nada.", errores);
    }

    public static ApiException noAutenticado(String mensaje) {
        return new ApiException(HttpStatus.UNAUTHORIZED, "NO_AUTENTICADO", mensaje, null);
    }

    public static ApiException prohibido(String mensaje) {
        return new ApiException(HttpStatus.FORBIDDEN, "ROL_SIN_PERMISO", mensaje, null);
    }

    public static ApiException noEncontrado(String mensaje) {
        return new ApiException(HttpStatus.NOT_FOUND, "NO_ENCONTRADO", mensaje, null);
    }

    public static ApiException conflicto(String mensaje) {
        return new ApiException(HttpStatus.CONFLICT, "CONFLICTO", mensaje, null);
    }

    public static ApiException reglaDeNegocio(String mensaje) {
        return new ApiException(HttpStatus.UNPROCESSABLE_ENTITY, "REGLA_DE_NEGOCIO", mensaje, null);
    }

    public HttpStatus getEstado() {
        return estado;
    }

    public String getCodigo() {
        return codigo;
    }

    public List<ApiError.Campo> getErrores() {
        return errores;
    }
}
