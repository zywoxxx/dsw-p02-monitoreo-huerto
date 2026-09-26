package mx.uv.dsw.huerto.service;

import java.io.Serializable;
import java.sql.SQLException;
import java.util.List;

import mx.uv.dsw.huerto.repository.AnotacionRepository;

/**
 * Caso de uso "Registrar anotacion" (RF06). En P02 estas reglas vivian en el servlet; en P03 se
 * concentran aqui para que la vista JSF solo presente. El rol llega de la sesion autenticada,
 * nunca de un campo del formulario.
 */
public class AnotacionService implements Serializable {

    private static final long serialVersionUID = 1L;

    private final AnotacionRepository repository;

    public AnotacionService() {
        this(new AnotacionRepository());
    }

    public AnotacionService(AnotacionRepository repository) {
        this.repository = repository;
    }

    /**
     * @return id de la anotacion creada
     * @throws ValidacionException entrada invalida (zona, lectura, rol o texto)
     * @throws SQLException        PostgreSQL no disponible
     */
    public long registrar(String zonaIdParam, String lecturaIdParam, String rolSesion, String textoParam)
            throws ValidacionException, SQLException {
        List<String> errores = LecturaValidator.nuevaListaErrores();
        Long zonaId = AnotacionValidator.parseZonaId(zonaIdParam, errores);
        Long lecturaId = AnotacionValidator.parseLecturaId(lecturaIdParam, errores);
        String rol = AnotacionValidator.parseRol(rolSesion, errores);
        String texto = AnotacionValidator.parseTexto(textoParam, errores);
        if (!errores.isEmpty()) {
            throw new ValidacionException(errores);
        }
        if (!repository.existeZona(zonaId)) {
            errores.add("La zona seleccionada no existe.");
        }
        if (lecturaId != null && !repository.existeLectura(lecturaId)) {
            errores.add("La lectura #" + lecturaId + " no existe.");
        }
        if (!errores.isEmpty()) {
            throw new ValidacionException(errores);
        }
        return repository.insert(zonaId, lecturaId, rol, texto);
    }
}
