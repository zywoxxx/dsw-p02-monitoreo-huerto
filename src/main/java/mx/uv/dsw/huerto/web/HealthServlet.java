package mx.uv.dsw.huerto.web;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import mx.uv.dsw.huerto.config.DbConfig;

/**
 * GET /health : ruta de salud (RF-07). Responde JSON con 200 si la aplicacion conecta a PostgreSQL
 * y 503 si faltan variables de entorno o la base no responde. No expone credenciales.
 */
@WebServlet(name = "HealthServlet", urlPatterns = {"/health"})
public class HealthServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.setContentType("application/json;charset=UTF-8");
        String version = null;
        long lecturas = -1;
        String error = null;

        if (!DbConfig.isConfigured()) {
            error = "Faltan variables DB_URL, DB_USER o DB_PASSWORD";
        } else {
            try (Connection cn = DbConfig.getConnection();
                 PreparedStatement ps = cn.prepareStatement("SELECT version(), (SELECT count(*) FROM lectura)");
                 ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    version = rs.getString(1);
                    lecturas = rs.getLong(2);
                }
            } catch (SQLException e) {
                error = e.getMessage();
            }
        }

        boolean up = error == null;
        resp.setStatus(up ? HttpServletResponse.SC_OK : HttpServletResponse.SC_SERVICE_UNAVAILABLE);
        try (PrintWriter out = resp.getWriter()) {
            out.print("{");
            out.print("\"status\":\"" + (up ? "UP" : "DOWN") + "\",");
            out.print("\"app\":\"web1 PRxx monitoreo de huerto\",");
            out.print("\"db\":\"" + (up ? "UP" : "DOWN") + "\",");
            out.print("\"dbUrl\":\"" + escape(DbConfig.urlForDisplay()) + "\",");
            if (up) {
                out.print("\"postgres\":\"" + escape(version) + "\",");
                out.print("\"lecturas\":" + lecturas);
            } else {
                out.print("\"error\":\"" + escape(error) + "\"");
            }
            out.print("}");
        }
    }

    private static String escape(String s) {
        if (s == null) {
            return "";
        }
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ").replace("\r", " ");
    }
}
