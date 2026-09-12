package mx.uv.dsw.huerto.web;

import java.io.IOException;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import mx.uv.dsw.huerto.model.Lectura;
import mx.uv.dsw.huerto.model.Sensor;
import mx.uv.dsw.huerto.repository.LecturaRepository;
import mx.uv.dsw.huerto.repository.SensorRepository;
import mx.uv.dsw.huerto.service.LecturaService;
import mx.uv.dsw.huerto.service.ValidacionException;

/**
 * Controlador del flujo principal (equivale al CatalogServlet del starter).
 *
 * <ul>
 *   <li>GET  /lecturas : catalogo de sensores + historial de lecturas (RF01, RF02, RF04, RF05).</li>
 *   <li>POST /lecturas : registra una lectura; 303 + redirect si es valida (RF03, RF06),
 *       400 con la lista de errores si no lo es (RF03, CA02).</li>
 * </ul>
 * La JSP solo presenta; las reglas viven en LecturaValidator/LecturaService y el SQL en los repositorios.
 */
@WebServlet(name = "LecturaServlet", urlPatterns = {"/lecturas"})
public class LecturaServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;
    private static final int LIMITE_LECTURAS = 20;
    private static final String VISTA = "/WEB-INF/views/lecturas.jsp";

    private final SensorRepository sensorRepository = new SensorRepository();
    private final LecturaRepository lecturaRepository = new LecturaRepository();
    private final LecturaService lecturaService = new LecturaService(sensorRepository, lecturaRepository);

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        // Mensaje de exito tras el patron POST-Redirect-GET
        String creada = req.getParameter("creada");
        if (creada != null && creada.matches("\\d{1,18}")) {
            req.setAttribute("mensajeOk", "Lectura #" + creada + " registrada correctamente.");
            String nivel = req.getParameter("alerta");
            if ("ALTA".equals(nivel) || "BAJA".equals(nivel)) {
                req.setAttribute("mensajeAlerta", "Se genero una alerta de nivel " + nivel
                    + " porque el valor esta fuera del umbral del sensor.");
            }
        }
        renderCatalogo(req, resp, Collections.emptyList(), HttpServletResponse.SC_OK);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");
        String sensorId = req.getParameter("sensorId");
        String valor = req.getParameter("valor");
        String observacion = req.getParameter("observacion");
        try {
            LecturaService.Resultado r = lecturaService.registrar(sensorId, valor, observacion);
            StringBuilder destino = new StringBuilder(req.getContextPath())
                .append("/lecturas?creada=").append(r.getLecturaId());
            if (r.getAlertaNivel() != null) {
                destino.append("&alerta=").append(r.getAlertaNivel());
            }
            resp.setStatus(HttpServletResponse.SC_SEE_OTHER);
            resp.setHeader("Location", destino.toString());
        } catch (ValidacionException e) {
            // Conserva lo capturado para que el usuario corrija sin volver a teclear
            req.setAttribute("formSensorId", sensorId);
            req.setAttribute("formValor", valor);
            req.setAttribute("formObservacion", observacion);
            renderCatalogo(req, resp, e.getErrores(), HttpServletResponse.SC_BAD_REQUEST);
        } catch (SQLException e) {
            throw new ServletException("Error de persistencia al registrar la lectura: " + e.getMessage(), e);
        }
    }

    private void renderCatalogo(HttpServletRequest req, HttpServletResponse resp, List<String> errores, int status)
            throws ServletException, IOException {
        try {
            List<Sensor> sensores = sensorRepository.findActivos();
            List<Lectura> lecturas = lecturaRepository.findRecientes(LIMITE_LECTURAS);
            req.setAttribute("sensores", sensores);
            req.setAttribute("lecturas", lecturas);
            req.setAttribute("errores", errores);
            resp.setStatus(status);
            resp.setContentType("text/html;charset=UTF-8");
            req.getRequestDispatcher(VISTA).forward(req, resp);
        } catch (SQLException e) {
            throw new ServletException("No fue posible consultar PostgreSQL: " + e.getMessage(), e);
        }
    }
}
