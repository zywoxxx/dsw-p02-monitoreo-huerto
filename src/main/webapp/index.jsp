<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%-- Pagina de entrada: delega al controlador del flujo principal (GET /lecturas). --%>
<% response.sendRedirect(request.getContextPath() + "/lecturas"); %>
