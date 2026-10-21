package mx.uv.dsw.huerto.api.zonas;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

/** Consultas del catalogo de zonas. SQL parametrizado; mismo esquema que P02/P03. */
@Repository
public class ZonaRepository {

    private static final String SELECT = "SELECT z.id, z.nombre, z.cultivo, z.ubicacion FROM zona z ";

    private final NamedParameterJdbcTemplate jdbc;

    public ZonaRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public List<Zona> listar() {
        return jdbc.query(SELECT + "ORDER BY z.nombre", new MapSqlParameterSource(), ZonaRepository::mapear);
    }

    public Optional<Zona> porId(long id) {
        return jdbc.query(SELECT + "WHERE z.id = :id", new MapSqlParameterSource("id", id), ZonaRepository::mapear)
            .stream().findFirst();
    }

    /** Zona del sensor que registro la lectura; vacio si la lectura no existe. */
    public Optional<Zona> porLectura(long lecturaId) {
        String sql = "SELECT z.id, z.nombre, z.cultivo, z.ubicacion "
            + "FROM lectura l "
            + "JOIN sensor s ON s.id = l.sensor_id "
            + "JOIN zona z   ON z.id = s.zona_id "
            + "WHERE l.id = :lecturaId";
        return jdbc.query(sql, new MapSqlParameterSource("lecturaId", lecturaId), ZonaRepository::mapear)
            .stream().findFirst();
    }

    private static Zona mapear(ResultSet rs, int fila) throws SQLException {
        Zona z = new Zona();
        z.setId(rs.getLong("id"));
        z.setNombre(rs.getString("nombre"));
        z.setCultivo(rs.getString("cultivo"));
        z.setUbicacion(rs.getString("ubicacion"));
        return z;
    }
}
