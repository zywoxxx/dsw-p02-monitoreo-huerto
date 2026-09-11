<%@ page contentType="text/html;charset=UTF-8" language="java" isErrorPage="true" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%-- Pagina de error generica: muestra el codigo HTTP y un mensaje sin exponer trazas ni credenciales. --%>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Error | PRxx Monitoreo de huerto</title>
  <link rel="stylesheet" href="${pageContext.request.contextPath}/css/estilos.css">
</head>
<body>
<header class="cabecera">
  <div class="contenedor">
    <h1>PRxx &middot; Monitoreo de huerto</h1>
    <nav><a href="${pageContext.request.contextPath}/lecturas">Volver a lecturas</a></nav>
  </div>
</header>
<main class="contenedor">
  <section class="tarjeta">
    <h2>Ocurrio un problema (HTTP <c:out value="${pageContext.errorData.statusCode}"/>)</h2>
    <c:choose>
      <c:when test="${pageContext.errorData.statusCode == 404}">
        <p>La ruta solicitada no existe en esta aplicacion.</p>
      </c:when>
      <c:otherwise>
        <p>No fue posible completar la operacion. Verifica que PostgreSQL este activo y que las variables
           <code>DB_URL</code>, <code>DB_USER</code> y <code>DB_PASSWORD</code> esten definidas en Tomcat.</p>
        <p class="ayuda">Detalle tecnico: <c:out value="${pageContext.exception.message}"/></p>
      </c:otherwise>
    </c:choose>
    <p><a href="${pageContext.request.contextPath}/health">Consultar ruta de salud</a></p>
  </section>
</main>
</body>
</html>
