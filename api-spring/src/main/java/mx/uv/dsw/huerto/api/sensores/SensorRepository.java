package mx.uv.dsw.huerto.api.sensores;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

/** Consultas de sensores con su zona, variable y umbral. SQL parametrizado; mismo esquema que P02/P03. */
@Repository
public class SensorRepository {

    private static final String BASE =
        "SELECT s.id, s.codigo, s.activo, s.zona_id, z.nombre AS zona, v.nombre AS variable, v.unidad, "
        + "       v.valor_minimo, v.valor_maximo, u.minimo AS umbral_min, u.maximo AS umbral_max "
        + "FROM sensor s "
        + "JOIN zona z        ON z.id = s.zona_id "
        + "JOIN variable v    ON v.id = s.variable_id "
        + "LEFT JOIN umbral u ON u.sensor_id = s.id ";

    private final NamedParameterJdbcTemplate jdbc;

    public SensorRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public List<Sensor> buscar(Long zonaId, Boolean activo) {
        MapSqlParameterSource p = new MapSqlParameterSource()
            .addValue("zonaId", zonaId, java.sql.Types.BIGINT)
            .addValue("activo", activo, java.sql.Types.BOOLEAN);
        String sql = BASE
            + "WHERE (CAST(:zonaId AS BIGINT) IS NULL OR s.zona_id = :zonaId) "
            + "  AND (CAST(:activo AS BOOLEAN) IS NULL OR s.activo = :activo) "
            + "ORDER BY z.nombre, s.codigo";
        return jdbc.query(sql, p, SensorRepository::mapear);
    }

    public Optional<Sensor> porId(long id) {
        List<Sensor> r = jdbc.query(BASE + "WHERE s.id = :id", new MapSqlParameterSource("id", id), SensorRepository::mapear);
        return r.stream().findFirst();
    }

    private static Sensor mapear(ResultSet rs, int fila) throws SQLException {
        Sensor s = new Sensor();
        s.setId(rs.getLong("id"));
        s.setCodigo(rs.getString("codigo"));
        s.setActivo(rs.getBoolean("activo"));
        s.setZonaId(rs.getLong("zona_id"));
        s.setZona(rs.getString("zona"));
        s.setVariable(rs.getString("variable"));
        s.setUnidad(rs.getString("unidad"));
        s.setRangoFisicoMinimo(rs.getBigDecimal("valor_minimo"));
        s.setRangoFisicoMaximo(rs.getBigDecimal("valor_maximo"));
        s.setUmbralMinimo(rs.getBigDecimal("umbral_min"));
        s.setUmbralMaximo(rs.getBigDecimal("umbral_max"));
        return s;
    }
}
