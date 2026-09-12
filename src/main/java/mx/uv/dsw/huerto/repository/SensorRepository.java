package mx.uv.dsw.huerto.repository;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import mx.uv.dsw.huerto.config.DbConfig;
import mx.uv.dsw.huerto.model.Sensor;

/**
 * Acceso JDBC a la tabla sensor y sus catalogos relacionados (zona, variable, umbral).
 * Todas las consultas son parametrizadas y cierran recursos con try-with-resources.
 */
public class SensorRepository {

    private static final String BASE_SELECT =
        "SELECT s.id, s.codigo, s.activo, s.zona_id, z.nombre AS zona, "
        + "       v.clave AS variable_clave, v.nombre AS variable_nombre, v.unidad, "
        + "       v.valor_minimo, v.valor_maximo, u.minimo AS umbral_min, u.maximo AS umbral_max "
        + "FROM sensor s "
        + "JOIN zona z        ON z.id = s.zona_id "
        + "JOIN variable v    ON v.id = s.variable_id "
        + "LEFT JOIN umbral u ON u.sensor_id = s.id ";

    /** RF01/RF02/RF04: sensores activos con zona, variable y umbral, ordenados por zona y codigo. */
    public List<Sensor> findActivos() throws SQLException {
        String sql = BASE_SELECT + "WHERE s.activo = TRUE ORDER BY z.nombre, s.codigo";
        List<Sensor> lista = new ArrayList<>();
        try (Connection cn = DbConfig.getConnection();
             PreparedStatement ps = cn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                lista.add(map(rs));
            }
        }
        return lista;
    }

    /** Busca un sensor por id dentro de una conexion ya abierta (se usa en la transaccion de registro). */
    public Optional<Sensor> findById(Connection cn, long id) throws SQLException {
        String sql = BASE_SELECT + "WHERE s.id = ?";
        try (PreparedStatement ps = cn.prepareStatement(sql)) {
            ps.setLong(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? Optional.of(map(rs)) : Optional.empty();
            }
        }
    }

    private Sensor map(ResultSet rs) throws SQLException {
        Sensor s = new Sensor();
        s.setId(rs.getLong("id"));
        s.setCodigo(rs.getString("codigo"));
        s.setActivo(rs.getBoolean("activo"));
        s.setZonaId(rs.getLong("zona_id"));
        s.setZona(rs.getString("zona"));
        s.setVariableClave(rs.getString("variable_clave"));
        s.setVariableNombre(rs.getString("variable_nombre"));
        s.setUnidad(rs.getString("unidad"));
        s.setValorMinimo(rs.getBigDecimal("valor_minimo"));
        s.setValorMaximo(rs.getBigDecimal("valor_maximo"));
        s.setUmbralMinimo(rs.getBigDecimal("umbral_min"));
        s.setUmbralMaximo(rs.getBigDecimal("umbral_max"));
        return s;
    }
}
