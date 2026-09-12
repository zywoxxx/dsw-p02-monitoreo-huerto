<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%-- Vista de alertas (RF-06). Solo presentacion; los datos los coloca AlertaServlet. --%>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Alertas | PR09 Monitoreo de huerto</title>
  <link rel="stylesheet" href="${pageContext.request.contextPath}/css/estilos.css">
</head>
<body>
<header class="cabecera">
  <div class="contenedor">
    <h1>PR09 &middot; Monitoreo de huerto o ambiente</h1>
    <p class="subtitulo">Incremento P02 &middot; JSP / Servlet 4.0 &middot; Tomcat 9 &middot; PostgreSQL 16</p>
    <nav>
      <a href="${pageContext.request.contextPath}/lecturas">Lecturas</a>
      <a class="activo" href="${pageContext.request.contextPath}/alertas">Alertas</a>
      <a href="${pageContext.request.contextPath}/anotaciones">Zonas y anotaciones</a>
      <a href="${pageContext.request.contextPath}/health">Salud (JSON)</a>
    </nav>
  </div>
</header>

<main class="contenedor">
  <section class="tarjeta">
    <h2>Alertas generadas (RF06)</h2>
    <p class="ayuda">Cada alerta nace de una lectura cuyo valor quedo fuera del umbral operativo del sensor (RF04).</p>
    <c:choose>
      <c:when test="${empty alertas}">
        <p class="vacio" id="sin-alertas">No hay alertas registradas.</p>
      </c:when>
      <c:otherwise>
        <div class="tabla-scroll">
          <table id="tabla-alertas">
            <thead>
              <tr><th>#</th><th>Lectura</th><th>Sensor</th><th>Zona</th><th>Valor</th>
                  <th>Nivel</th><th>Mensaje</th><th>Atendida</th><th>Creada</th></tr>
            </thead>
            <tbody>
              <c:forEach var="a" items="${alertas}">
                <tr class="fila-alerta">
                  <td>${a.id}</td>
                  <td>#${a.lecturaId}</td>
                  <td><code><c:out value="${a.sensorCodigo}"/></code></td>
                  <td><c:out value="${a.zona}"/></td>
                  <td class="num"><c:out value="${a.valor}"/> <c:out value="${a.unidad}"/></td>
                  <td><span class="etiqueta etiqueta-${a.nivel}"><c:out value="${a.nivel}"/></span></td>
                  <td><c:out value="${a.mensaje}"/></td>
                  <td>${a.atendida ? 'Si' : 'No'}</td>
                  <td><c:out value="${a.creadaEnTexto}"/></td>
                </tr>
              </c:forEach>
            </tbody>
          </table>
        </div>
      </c:otherwise>
    </c:choose>
  </section>
</main>

<footer class="pie contenedor">
  Desarrollo de Sistemas Web &middot; DSW-19559 &middot; Datos ficticios de laboratorio.
</footer>
</body>
</html>
