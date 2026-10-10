package mx.uv.dsw.huerto.api.lecturas;

import java.math.BigDecimal;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

/** Acceso JDBC a lectura y alerta. Las escrituras participan en la transaccion que abre LecturaService. */
@Repository
public class LecturaRepository {

    private static final String SELECT =
        "SELECT l.id, l.sensor_id, s.codigo, v.nombre AS variable, v.unidad, z.nombre AS zona, "
        + "       l.valor, l.origen, l.observacion, l.registrado_en, a.nivel, a.mensaje "
        + "FROM lectura l "
        + "JOIN sensor s      ON s.id = l.sensor_id "
        + "JOIN variable v    ON v.id = s.variable_id "
        + "JOIN zona z        ON z.id = s.zona_id "
        + "LEFT JOIN alerta a ON a.lectura_id = l.id ";

    private static final String FILTRO =
        "WHERE (CAST(:sensorId AS BIGINT) IS NULL OR l.sensor_id = :sensorId) "
        + "  AND (CAST(:zonaId AS BIGINT) IS NULL OR s.zona_id = :zonaId) "
        + "  AND (CAST(:origen AS VARCHAR) IS NULL OR l.origen = :origen) ";

    private final NamedParameterJdbcTemplate jdbc;

    public LecturaRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private static MapSqlParameterSource filtros(Long sensorId, Long zonaId, String origen) {
        return new MapSqlParameterSource()
            .addValue("sensorId", sensorId, Types.BIGINT)
            .addValue("zonaId", zonaId, Types.BIGINT)
            .addValue("origen", origen, Types.VARCHAR);
    }

    public List<Lectura> buscar(Long sensorId, Long zonaId, String origen, int tamano, int desplazamiento) {
        MapSqlParameterSource p = filtros(sensorId, zonaId, origen)
            .addValue("limite", tamano).addValue("desplazamiento", desplazamiento);
        return jdbc.query(SELECT + FILTRO + "ORDER BY l.registrado_en DESC, l.id DESC LIMIT :limite OFFSET :desplazamiento",
            p, LecturaRepository::mapear);
    }

    public long contar(Long sensorId, Long zonaId, String origen) {
        Long total = jdbc.queryForObject(
            "SELECT count(*) FROM lectura l JOIN sensor s ON s.id = l.sensor_id " + FILTRO,
            filtros(sensorId, zonaId, origen), Long.class);
        return total == null ? 0 : total;
    }

    public Optional<Lectura> porId(long id) {
        return jdbc.query(SELECT + "WHERE l.id = :id", new MapSqlParameterSource("id", id), LecturaRepository::mapear)
            .stream().findFirst();
    }

    public long insertarLectura(long sensorId, BigDecimal valor, String observacion) {
        Long id = jdbc.queryForObject(
            "INSERT INTO lectura (sensor_id, valor, origen, observacion) VALUES (:sensorId, :valor, 'manual', :obs) RETURNING id",
            new MapSqlParameterSource().addValue("sensorId", sensorId).addValue("valor", valor)
                .addValue("obs", observacion, Types.VARCHAR), Long.class);
        return id == null ? 0 : id;
    }

    public void insertarAlerta(long lecturaId, String nivel, String mensaje) {
        jdbc.update("INSERT INTO alerta (lectura_id, nivel, mensaje) VALUES (:lecturaId, :nivel, :mensaje)",
            new MapSqlParameterSource().addValue("lecturaId", lecturaId).addValue("nivel", nivel).addValue("mensaje", mensaje));
    }

    private static Lectura mapear(ResultSet rs, int fila) throws SQLException {
        Lectura l = new Lectura();
        l.setId(rs.getLong("id"));
        l.setSensorId(rs.getLong("sensor_id"));
        l.setSensorCodigo(rs.getString("codigo"));
        l.setVariable(rs.getString("variable"));
        l.setUnidad(rs.getString("unidad"));
        l.setZona(rs.getString("zona"));
        l.setValor(rs.getBigDecimal("valor"));
        l.setOrigen(rs.getString("origen"));
        l.setObservacion(rs.getString("observacion"));
        l.setRegistradoEn(rs.getObject("registrado_en", OffsetDateTime.class));
        String nivel = rs.getString("nivel");
        if (nivel != null) {
            l.setAlerta(new Lectura.AlertaResumen(nivel, rs.getString("mensaje")));
        }
        return l;
    }
}
