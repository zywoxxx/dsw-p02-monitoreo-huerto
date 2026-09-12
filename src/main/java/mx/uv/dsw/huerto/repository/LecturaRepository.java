package mx.uv.dsw.huerto.repository;

import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;

import mx.uv.dsw.huerto.config.DbConfig;
import mx.uv.dsw.huerto.model.Alerta;
import mx.uv.dsw.huerto.model.Lectura;

/**
 * Acceso JDBC a las tablas lectura y alerta.
 * Equivale al CatalogRepository del starter, adaptado al dominio PR09 (huerto).
 * Solo SQL parametrizado; ninguna cadena del usuario se concatena en la consulta.
 */
public class LecturaRepository {

    /** RF05 (historial): lecturas mas recientes con datos del sensor y nivel de alerta si existe. */
    public List<Lectura> findRecientes(int limite) throws SQLException {
        String sql =
            "SELECT l.id, l.sensor_id, s.codigo, v.nombre AS variable_nombre, v.unidad, z.nombre AS zona, "
            + "       l.valor, l.origen, l.observacion, l.registrado_en, a.nivel "
            + "FROM lectura l "
            + "JOIN sensor s      ON s.id = l.sensor_id "
            + "JOIN variable v    ON v.id = s.variable_id "
            + "JOIN zona z        ON z.id = s.zona_id "
            + "LEFT JOIN alerta a ON a.lectura_id = l.id "
            + "ORDER BY l.registrado_en DESC, l.id DESC "
            + "LIMIT ?";
        List<Lectura> lista = new ArrayList<>();
        try (Connection cn = DbConfig.getConnection();
             PreparedStatement ps = cn.prepareStatement(sql)) {
            ps.setInt(1, limite);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    Lectura l = new Lectura();
                    l.setId(rs.getLong("id"));
                    l.setSensorId(rs.getLong("sensor_id"));
                    l.setSensorCodigo(rs.getString("codigo"));
                    l.setVariableNombre(rs.getString("variable_nombre"));
                    l.setUnidad(rs.getString("unidad"));
                    l.setZona(rs.getString("zona"));
                    l.setValor(rs.getBigDecimal("valor"));
                    l.setOrigen(rs.getString("origen"));
                    l.setObservacion(rs.getString("observacion"));
                    l.setRegistradoEn(rs.getObject("registrado_en", OffsetDateTime.class));
                    l.setAlertaNivel(rs.getString("nivel"));
                    lista.add(l);
                }
            }
        }
        return lista;
    }

    /** Cuenta total de lecturas; se usa para demostrar persistencia en /health. */
    public long count() throws SQLException {
        try (Connection cn = DbConfig.getConnection();
             PreparedStatement ps = cn.prepareStatement("SELECT count(*) FROM lectura");
             ResultSet rs = ps.executeQuery()) {
            rs.next();
            return rs.getLong(1);
        }
    }

    /** RF03: inserta una lectura dentro de la conexion/transaccion recibida y devuelve su id. */
    public long insertLectura(Connection cn, long sensorId, BigDecimal valor, String observacion)
            throws SQLException {
        String sql = "INSERT INTO lectura (sensor_id, valor, origen, observacion) VALUES (?, ?, 'manual', ?) RETURNING id";
        try (PreparedStatement ps = cn.prepareStatement(sql)) {
            ps.setLong(1, sensorId);
            ps.setBigDecimal(2, valor);
            ps.setString(3, observacion);
            try (ResultSet rs = ps.executeQuery()) {
                rs.next();
                return rs.getLong(1);
            }
        }
    }

    /** RF06: inserta la alerta asociada a una lectura fuera de umbral. */
    public long insertAlerta(Connection cn, long lecturaId, String nivel, String mensaje) throws SQLException {
        String sql = "INSERT INTO alerta (lectura_id, nivel, mensaje) VALUES (?, ?, ?) RETURNING id";
        try (PreparedStatement ps = cn.prepareStatement(sql)) {
            ps.setLong(1, lecturaId);
            ps.setString(2, nivel);
            ps.setString(3, mensaje);
            try (ResultSet rs = ps.executeQuery()) {
                rs.next();
                return rs.getLong(1);
            }
        }
    }

    /** RF06: alertas mas recientes, primero las no atendidas. */
    public List<Alerta> findAlertas(int limite) throws SQLException {
        String sql =
            "SELECT a.id, a.lectura_id, s.codigo, z.nombre AS zona, l.valor, v.unidad, "
            + "       a.nivel, a.mensaje, a.atendida, a.creada_en "
            + "FROM alerta a "
            + "JOIN lectura l     ON l.id = a.lectura_id "
            + "JOIN sensor s      ON s.id = l.sensor_id "
            + "JOIN variable v    ON v.id = s.variable_id "
            + "JOIN zona z        ON z.id = s.zona_id "
            + "ORDER BY a.atendida ASC, a.creada_en DESC "
            + "LIMIT ?";
        List<Alerta> lista = new ArrayList<>();
        try (Connection cn = DbConfig.getConnection();
             PreparedStatement ps = cn.prepareStatement(sql)) {
            ps.setInt(1, limite);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    Alerta a = new Alerta();
                    a.setId(rs.getLong("id"));
                    a.setLecturaId(rs.getLong("lectura_id"));
                    a.setSensorCodigo(rs.getString("codigo"));
                    a.setZona(rs.getString("zona"));
                    a.setValor(rs.getBigDecimal("valor"));
                    a.setUnidad(rs.getString("unidad"));
                    a.setNivel(rs.getString("nivel"));
                    a.setMensaje(rs.getString("mensaje"));
                    a.setAtendida(rs.getBoolean("atendida"));
                    a.setCreadaEn(rs.getObject("creada_en", OffsetDateTime.class));
                    lista.add(a);
                }
            }
        }
        return lista;
    }
}
