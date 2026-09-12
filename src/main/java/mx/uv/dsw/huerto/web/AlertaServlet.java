package mx.uv.dsw.huerto.web;

import java.io.IOException;
import java.sql.SQLException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import mx.uv.dsw.huerto.repository.LecturaRepository;

/** GET /alertas : lista las alertas generadas por lecturas fuera de umbral (RF06). */
@WebServlet(name = "AlertaServlet", urlPatterns = {"/alertas"})
public class AlertaServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;
    private static final int LIMITE = 50;

    private final LecturaRepository lecturaRepository = new LecturaRepository();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            req.setAttribute("alertas", lecturaRepository.findAlertas(LIMITE));
            resp.setContentType("text/html;charset=UTF-8");
            req.getRequestDispatcher("/WEB-INF/views/alertas.jsp").forward(req, resp);
        } catch (SQLException e) {
            throw new ServletException("No fue posible consultar las alertas: " + e.getMessage(), e);
        }
    }
}
