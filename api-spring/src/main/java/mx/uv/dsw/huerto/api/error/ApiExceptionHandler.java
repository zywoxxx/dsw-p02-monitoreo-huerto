package mx.uv.dsw.huerto.api.error;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.transaction.TransactionException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

/** Traduce excepciones a respuestas JSON con el esquema "Error" del contrato. Nunca envia trazas. */
@RestControllerAdvice
public class ApiExceptionHandler {

    private static final Logger LOG = LoggerFactory.getLogger(ApiExceptionHandler.class);

    @ExceptionHandler(ApiException.class)
    public ResponseEntity<ApiError> api(ApiException e) {
        return ResponseEntity.status(e.getEstado()).body(new ApiError(e.getCodigo(), e.getMessage(), e.getErrores()));
    }

    /** JSON mal formado o un valor que no es del tipo esperado (por ejemplo "valor": "abc"). */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ApiError> ilegible(HttpMessageNotReadableException e) {
        return ResponseEntity.badRequest().body(new ApiError("VALIDACION",
            "El cuerpo de la peticion no es un JSON valido o algun campo no tiene el tipo esperado.",
            List.of(new ApiError.Campo("cuerpo", "Revisa que cada campo tenga el tipo del contrato: numeros como 'valor', enteros como 'sensorId', booleanos como 'atendida'."))));
    }

    @ExceptionHandler({MethodArgumentTypeMismatchException.class, MissingServletRequestParameterException.class})
    public ResponseEntity<ApiError> parametro(Exception e) {
        return ResponseEntity.badRequest().body(new ApiError("VALIDACION", "Parametro de consulta invalido o faltante."));
    }

    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<ApiError> metodo(HttpRequestMethodNotSupportedException e) {
        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED)
            .body(new ApiError("METODO_NO_PERMITIDO", "El metodo " + e.getMethod() + " no esta disponible en esta ruta."));
    }

    /**
     * PostgreSQL no responde o rechazo la operacion: 503 para que el cliente sepa que puede reintentar.
     * TransactionException cubre el caso en que ni siquiera se pudo abrir la transaccion (base detenida).
     */
    @ExceptionHandler({DataAccessException.class, TransactionException.class})
    public ResponseEntity<ApiError> datos(RuntimeException e) {
        LOG.error("Fallo de acceso a datos", e);
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
            .body(new ApiError("BASE_NO_DISPONIBLE", "No fue posible completar la operacion en PostgreSQL; no se guardo nada."));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiError> inesperado(Exception e) {
        LOG.error("Error inesperado", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ApiError("ERROR_INTERNO", "Ocurrio un error inesperado."));
    }
}
