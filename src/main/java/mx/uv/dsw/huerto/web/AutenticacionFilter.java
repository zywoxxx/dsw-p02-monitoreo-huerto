package mx.uv.dsw.huerto.web;

import java.io.IOException;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

/**
 * Protege las vistas de /app/*: sin sesion autenticada no se sirve ninguna pagina del flujo.
 * Para peticiones AJAX de JSF responde con una redireccion en formato partial-response, que es
 * lo que jsf.js entiende; una redireccion HTTP normal rompe la respuesta parcial.
 */
@WebFilter(urlPatterns = {"/app/*"})
public class AutenticacionFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse resp = (HttpServletResponse) response;
        HttpSession session = req.getSession(false);
        boolean autenticado = session != null && session.getAttribute(SesionBean.ATRIBUTO_USUARIO) != null;
        if (autenticado) {
            chain.doFilter(request, response);
            return;
        }
        String destino = req.getContextPath() + "/login.xhtml?expirada=1";
        if ("partial/ajax".equals(req.getHeader("Faces-Request"))) {
            resp.setContentType("text/xml;charset=UTF-8");
            resp.setHeader("Cache-Control", "no-cache");
            resp.getWriter().print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                + "<partial-response><redirect url=\"" + destino + "\"/></partial-response>");
        } else {
            resp.sendRedirect(destino);
        }
    }
}
