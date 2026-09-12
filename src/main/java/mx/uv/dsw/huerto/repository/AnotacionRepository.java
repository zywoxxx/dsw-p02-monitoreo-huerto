package mx.uv.dsw.huerto.repository;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;

import mx.uv.dsw.huerto.config.DbConfig;
import mx.uv.dsw.huerto.model.Anotacion;
import mx.uv.dsw.huerto.model.Zona;

/** Acceso JDBC parametrizado a las tablas zona y anotacion (RF01, RF06). */
public class AnotacionRepository {

    /** RF01: zonas del huerto ordenadas por nombre. */
    public List<Zona> findZonas() throws SQLException {
        String sql = "SELECT id, nombre, cultivo, ubicacion FROM zona ORDER BY nombre";
        List<Zona> lista = new ArrayList<>();
        try (Connection cn = DbConfig.getConnection();
             PreparedStatement ps = cn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Zona z = new Zona();
                z.setId(rs.getLong("id"));
                z.setNombre(rs.getString("nombre"));
                z.setCultivo(rs.getString("cultivo"));
                z.setUbicacion(rs.getString("ubicacion"));
                lista.add(z);
            }
        }
        return lista;
    }

    /** Comprueba que la zona exista (validacion semantica del POST). */
    public boolean existeZona(long zonaId) throws SQLException {
        try (Connection cn = DbConfig.getConnection();
             PreparedStatement ps = cn.prepareStatement("SELECT 1 FROM zona WHERE id = ?")) {
            ps.setLong(1, zonaId);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next();
            }
        }
    }

    /** Comprueba que la lectura exista (si la anotacion se asocia a una lectura). */
    public boolean existeLectura(long lecturaId) throws SQLException {
        try (Connection cn = DbConfig.getConnection();
             PreparedStatement ps = cn.prepareStatement("SELECT 1 FROM lectura WHERE id = ?")) {
            ps.setLong(1, lecturaId);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next();
            }
        }
    }

    /** RF06: inserta una anotacion y devuelve su id. */
    public long insert(long zonaId, Long lecturaId, String autorRol, String texto) throws SQLException {
        String sql = "INSERT INTO anotacion (zona_id, lectura_id, autor_rol, texto) VALUES (?, ?, ?, ?) RETURNING id";
        try (Connection cn = DbConfig.getConnection();
             PreparedStatement ps = cn.prepareStatement(sql)) {
            ps.setLong(1, zonaId);
            if (lecturaId == null) {
                ps.setNull(2, Types.BIGINT);
            } else {
                ps.setLong(2, lecturaId);
            }
            ps.setString(3, autorRol);
            ps.setString(4, texto);
            try (ResultSet rs = ps.executeQuery()) {
                rs.next();
                return rs.getLong(1);
            }
        }
    }

    /** RF06: anotaciones mas recientes con el nombre de su zona. */
    public List<Anotacion> findRecientes(int limite) throws SQLException {
        String sql =
            "SELECT n.id, n.zona_id, z.nombre AS zona, n.lectura_id, n.autor_rol, n.texto, n.creada_en "
            + "FROM anotacion n JOIN zona z ON z.id = n.zona_id "
            + "ORDER BY n.creada_en DESC, n.id DESC LIMIT ?";
        List<Anotacion> lista = new ArrayList<>();
        try (Connection cn = DbConfig.getConnection();
             PreparedStatement ps = cn.prepareStatement(sql)) {
            ps.setInt(1, limite);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    Anotacion n = new Anotacion();
                    n.setId(rs.getLong("id"));
                    n.setZonaId(rs.getLong("zona_id"));
                    n.setZona(rs.getString("zona"));
                    long lid = rs.getLong("lectura_id");
                    n.setLecturaId(rs.wasNull() ? null : lid);
                    n.setAutorRol(rs.getString("autor_rol"));
                    n.setTexto(rs.getString("texto"));
                    n.setCreadaEn(rs.getObject("creada_en", OffsetDateTime.class));
                    lista.add(n);
                }
            }
        }
        return lista;
    }
}
