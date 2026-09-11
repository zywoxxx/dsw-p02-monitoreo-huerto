package mx.uv.dsw.huerto.config;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Configuracion de acceso a PostgreSQL externalizada por entorno.
 *
 * <p>Las credenciales NUNCA se escriben en el codigo ni en el WAR. Se leen, en este orden:
 * <ol>
 *   <li>Propiedades de sistema de la JVM: {@code -DDB_URL=... -DDB_USER=... -DDB_PASSWORD=...}</li>
 *   <li>Variables de entorno: {@code DB_URL}, {@code DB_USER}, {@code DB_PASSWORD}</li>
 * </ol>
 * En Tomcat se definen en {@code bin/setenv.bat} o {@code bin/setenv.sh} (ver README).
 */
public final class DbConfig {

    public static final String KEY_URL = "DB_URL";
    public static final String KEY_USER = "DB_USER";
    public static final String KEY_PASSWORD = "DB_PASSWORD";

    private DbConfig() {
    }

    /** Lee una clave de configuracion; primero -Dclave de la JVM, luego variable de entorno. */
    public static String read(String key) {
        String value = System.getProperty(key);
        if (value == null || value.isBlank()) {
            value = System.getenv(key);
        }
        return value == null ? null : value.trim();
    }

    /** Indica si las tres variables obligatorias estan presentes. */
    public static boolean isConfigured() {
        return notBlank(read(KEY_URL)) && notBlank(read(KEY_USER)) && read(KEY_PASSWORD) != null;
    }

    /** URL JDBC sin credenciales; se usa solo para diagnostico en /health. */
    public static String urlForDisplay() {
        String url = read(KEY_URL);
        return url == null ? "(no configurada)" : url;
    }

    /**
     * Abre una conexion JDBC. El llamador debe cerrarla (try-with-resources).
     *
     * @throws SQLException si faltan variables o PostgreSQL no responde.
     */
    public static Connection getConnection() throws SQLException {
        if (!isConfigured()) {
            throw new SQLException("Faltan variables de entorno DB_URL, DB_USER o DB_PASSWORD");
        }
        try {
            Class.forName("org.postgresql.Driver");
        } catch (ClassNotFoundException e) {
            throw new SQLException("Driver JDBC de PostgreSQL no encontrado en el WAR", e);
        }
        return DriverManager.getConnection(read(KEY_URL), read(KEY_USER), read(KEY_PASSWORD));
    }

    private static boolean notBlank(String s) {
        return s != null && !s.isBlank();
    }
}
