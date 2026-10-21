package mx.uv.dsw.huerto.api.anotaciones;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

/** Acceso JDBC a anotacion. La escritura participa en la transaccion que abre AnotacionService. */
@Repository
public class AnotacionRepository {

    private static final String SELECT =
        "SELECT n.id, n.zona_id, z.nombre AS zona, n.lectura_id, n.autor_rol, n.texto, n.creada_en "
        + "FROM anotacion n "
        + "JOIN zona z ON z.id = n.zona_id ";

    private static final String FILTRO = "WHERE (CAST(:zonaId AS BIGINT) IS NULL OR n.zona_id = :zonaId) ";

    private final NamedParameterJdbcTemplate jdbc;

    public AnotacionRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private static MapSqlParameterSource filtros(Long zonaId) {
        return new MapSqlParameterSource().addValue("zonaId", zonaId, Types.BIGINT);
    }

    public List<Anotacion> buscar(Long zonaId, int tamano, int desplazamiento) {
        MapSqlParameterSource p = filtros(zonaId).addValue("limite", tamano).addValue("desplazamiento", desplazamiento);
        return jdbc.query(SELECT + FILTRO + "ORDER BY n.creada_en DESC, n.id DESC LIMIT :limite OFFSET :desplazamiento",
            p, AnotacionRepository::mapear);
    }

    public long contar(Long zonaId) {
        Long total = jdbc.queryForObject("SELECT count(*) FROM anotacion n " + FILTRO, filtros(zonaId), Long.class);
        return total == null ? 0 : total;
    }

    public Optional<Anotacion> porId(long id) {
        return jdbc.query(SELECT + "WHERE n.id = :id", new MapSqlParameterSource("id", id), AnotacionRepository::mapear)
            .stream().findFirst();
    }

    public long insertar(long zonaId, Long lecturaId, String autorRol, String texto) {
        Long id = jdbc.queryForObject(
            "INSERT INTO anotacion (zona_id, lectura_id, autor_rol, texto) VALUES (:zonaId, :lecturaId, :autorRol, :texto) RETURNING id",
            new MapSqlParameterSource().addValue("zonaId", zonaId).addValue("lecturaId", lecturaId, Types.BIGINT)
                .addValue("autorRol", autorRol).addValue("texto", texto), Long.class);
        return id == null ? 0 : id;
    }

    private static Anotacion mapear(ResultSet rs, int fila) throws SQLException {
        Anotacion n = new Anotacion();
        n.setId(rs.getLong("id"));
        n.setZonaId(rs.getLong("zona_id"));
        n.setZona(rs.getString("zona"));
        n.setLecturaId(rs.getObject("lectura_id", Long.class));
        n.setAutorRol(rs.getString("autor_rol"));
        n.setTexto(rs.getString("texto"));
        n.setCreadaEn(rs.getObject("creada_en", OffsetDateTime.class));
        return n;
    }
}
