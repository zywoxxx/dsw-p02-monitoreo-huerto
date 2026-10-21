package mx.uv.dsw.huerto.api.alertas;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

/** Acceso JDBC a alerta. La escritura participa en la transaccion que abre AlertaService. */
@Repository
public class AlertaRepository {

    private static final String SELECT =
        "SELECT a.id, a.lectura_id, s.codigo, v.nombre AS variable, s.zona_id, z.nombre AS zona, "
        + "       l.valor, v.unidad, a.nivel, a.mensaje, a.atendida, a.atendida_en, a.atendida_por, a.creada_en "
        + "FROM alerta a "
        + "JOIN lectura l  ON l.id = a.lectura_id "
        + "JOIN sensor s   ON s.id = l.sensor_id "
        + "JOIN variable v ON v.id = s.variable_id "
        + "JOIN zona z     ON z.id = s.zona_id ";

    private static final String FILTRO =
        "WHERE (CAST(:nivel AS VARCHAR) IS NULL OR a.nivel = :nivel) "
        + "  AND (CAST(:atendida AS BOOLEAN) IS NULL OR a.atendida = :atendida) "
        + "  AND (CAST(:zonaId AS BIGINT) IS NULL OR s.zona_id = :zonaId) ";

    private final NamedParameterJdbcTemplate jdbc;

    public AlertaRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private static MapSqlParameterSource filtros(String nivel, Boolean atendida, Long zonaId) {
        return new MapSqlParameterSource()
            .addValue("nivel", nivel, Types.VARCHAR)
            .addValue("atendida", atendida, Types.BOOLEAN)
            .addValue("zonaId", zonaId, Types.BIGINT);
    }

    public List<Alerta> buscar(String nivel, Boolean atendida, Long zonaId, int tamano, int desplazamiento) {
        MapSqlParameterSource p = filtros(nivel, atendida, zonaId)
            .addValue("limite", tamano).addValue("desplazamiento", desplazamiento);
        return jdbc.query(SELECT + FILTRO + "ORDER BY a.creada_en DESC, a.id DESC LIMIT :limite OFFSET :desplazamiento",
            p, AlertaRepository::mapear);
    }

    public long contar(String nivel, Boolean atendida, Long zonaId) {
        Long total = jdbc.queryForObject(
            "SELECT count(*) FROM alerta a JOIN lectura l ON l.id = a.lectura_id JOIN sensor s ON s.id = l.sensor_id " + FILTRO,
            filtros(nivel, atendida, zonaId), Long.class);
        return total == null ? 0 : total;
    }

    public Optional<Alerta> porId(long id) {
        return jdbc.query(SELECT + "WHERE a.id = :id", new MapSqlParameterSource("id", id), AlertaRepository::mapear)
            .stream().findFirst();
    }

    /**
     * Cambia el estado de atencion. El instante y el rol los pone el servidor: now() y el rol del token
     * al atender, NULL al reabrir (asi lo exige ck_alerta_atencion). Solo escribe si la alerta sigue en
     * el estado contrario al pedido, para que dos peticiones simultaneas no la atiendan las dos.
     *
     * @return filas cambiadas: 1 si se cambio el estado, 0 si ya estaba en el estado pedido
     */
    public int actualizarAtencion(long id, boolean atendida, String rol) {
        return jdbc.update("UPDATE alerta SET atendida = :atendida, "
                + "atendida_en = CASE WHEN CAST(:atendida AS BOOLEAN) THEN now() ELSE NULL END, "
                + "atendida_por = :rol "
                + "WHERE id = :id AND atendida = NOT CAST(:atendida AS BOOLEAN)",
            new MapSqlParameterSource().addValue("atendida", atendida)
                .addValue("rol", atendida ? rol : null, Types.VARCHAR).addValue("id", id));
    }

    private static Alerta mapear(ResultSet rs, int fila) throws SQLException {
        Alerta a = new Alerta();
        a.setId(rs.getLong("id"));
        a.setLecturaId(rs.getLong("lectura_id"));
        a.setSensorCodigo(rs.getString("codigo"));
        a.setVariable(rs.getString("variable"));
        a.setZonaId(rs.getLong("zona_id"));
        a.setZona(rs.getString("zona"));
        a.setValor(rs.getBigDecimal("valor"));
        a.setUnidad(rs.getString("unidad"));
        a.setNivel(rs.getString("nivel"));
        a.setMensaje(rs.getString("mensaje"));
        a.setAtendida(rs.getBoolean("atendida"));
        a.setAtendidaEn(rs.getObject("atendida_en", OffsetDateTime.class));
        a.setAtendidaPor(rs.getString("atendida_por"));
        a.setCreadaEn(rs.getObject("creada_en", OffsetDateTime.class));
        return a;
    }
}
