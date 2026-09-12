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

import mx.uv.dsw.huerto.repository.AnotacionRepository;
import mx.uv.dsw.huerto.service.AnotacionValidator;
import mx.uv.dsw.huerto.service.LecturaValidator;

/**
 * RF06 (anotaciones) y RF01 (zonas).
 * <ul>
 *   <li>GET  /anotaciones : zonas del huerto y anotaciones recientes.</li>
 *   <li>POST /anotaciones : registra una anotacion; 303 si es valida, 400 con errores si no.</li>
 * </ul>
 */
@WebServlet(name = "AnotacionServlet", urlPatterns = {"/anotaciones"})
public class AnotacionServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;
    private static final int LIMITE = 20;
    private static final String VISTA = "/WEB-INF/views/anotaciones.jsp";

    private final AnotacionRepository repository = new AnotacionRepository();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        String creada = req.getParameter("creada");
        if (creada != null && creada.matches("\\d{1,18}")) {
            req.setAttribute("mensajeOk", "Anotacion #" + creada + " registrada correctamente.");
        }
        render(req, resp, Collections.emptyList(), HttpServletResponse.SC_OK);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");
        String zonaParam = req.getParameter("zonaId");
        String lecturaParam = req.getParameter("lecturaId");
        String rolParam = req.getParameter("autorRol");
        String textoParam = req.getParameter("texto");

        List<String> errores = LecturaValidator.nuevaListaErrores();
        Long zonaId = AnotacionValidator.parseZonaId(zonaParam, errores);
        Long lecturaId = AnotacionValidator.parseLecturaId(lecturaParam, errores);
        String rol = AnotacionValidator.parseRol(rolParam, errores);
        String texto = AnotacionValidator.parseTexto(textoParam, errores);

        try {
            if (errores.isEmpty()) {
                if (!repository.existeZona(zonaId)) {
                    errores.add("La zona seleccionada no existe.");
                }
                if (lecturaId != null && !repository.existeLectura(lecturaId)) {
                    errores.add("La lectura #" + lecturaId + " no existe.");
                }
            }
            if (!errores.isEmpty()) {
                req.setAttribute("formZonaId", zonaParam);
                req.setAttribute("formLecturaId", lecturaParam);
                req.setAttribute("formAutorRol", rolParam);
                req.setAttribute("formTexto", textoParam);
                render(req, resp, errores, HttpServletResponse.SC_BAD_REQUEST);
                return;
            }
            long id = repository.insert(zonaId, lecturaId, rol, texto);
            resp.setStatus(HttpServletResponse.SC_SEE_OTHER);
            resp.setHeader("Location", req.getContextPath() + "/anotaciones?creada=" + id);
        } catch (SQLException e) {
            throw new ServletException("Error de persistencia al registrar la anotacion: " + e.getMessage(), e);
        }
    }

    private void render(HttpServletRequest req, HttpServletResponse resp, List<String> errores, int status)
            throws ServletException, IOException {
        try {
            req.setAttribute("zonas", repository.findZonas());
            req.setAttribute("anotaciones", repository.findRecientes(LIMITE));
            req.setAttribute("roles", AnotacionValidator.ROLES);
            req.setAttribute("errores", errores);
            resp.setStatus(status);
            resp.setContentType("text/html;charset=UTF-8");
            req.getRequestDispatcher(VISTA).forward(req, resp);
        } catch (SQLException e) {
            throw new ServletException("No fue posible consultar PostgreSQL: " + e.getMessage(), e);
        }
    }
}
