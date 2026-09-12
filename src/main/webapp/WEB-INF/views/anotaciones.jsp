<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%-- Vista de zonas (RF01) y anotaciones (RF06). Solo presentacion; los datos los coloca AnotacionServlet. --%>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Anotaciones | PR09 Monitoreo de huerto</title>
  <link rel="stylesheet" href="${pageContext.request.contextPath}/css/estilos.css">
</head>
<body>
<header class="cabecera">
  <div class="contenedor">
    <h1>PR09 &middot; Monitoreo de huerto o ambiente</h1>
    <p class="subtitulo">Incremento P02 &middot; JSP / Servlet 4.0 &middot; Tomcat 9 &middot; PostgreSQL 16</p>
    <nav>
      <a href="${pageContext.request.contextPath}/lecturas">Lecturas</a>
      <a href="${pageContext.request.contextPath}/alertas">Alertas</a>
      <a class="activo" href="${pageContext.request.contextPath}/anotaciones">Zonas y anotaciones</a>
      <a href="${pageContext.request.contextPath}/health">Salud (JSON)</a>
    </nav>
  </div>
</header>

<main class="contenedor">

  <c:if test="${not empty mensajeOk}">
    <div class="aviso aviso-ok" id="aviso-ok"><c:out value="${mensajeOk}"/></div>
  </c:if>
  <c:if test="${not empty errores}">
    <div class="aviso aviso-error" id="aviso-error">
      <strong>La anotacion no se registro. Corrige lo siguiente:</strong>
      <ul>
        <c:forEach var="e" items="${errores}">
          <li><c:out value="${e}"/></li>
        </c:forEach>
      </ul>
    </div>
  </c:if>

  <section class="tarjeta">
    <h2>Zonas del huerto (RF01)</h2>
    <div class="tabla-scroll">
      <table id="tabla-zonas">
        <thead><tr><th>#</th><th>Zona</th><th>Cultivo</th><th>Ubicacion</th></tr></thead>
        <tbody>
          <c:forEach var="z" items="${zonas}">
            <tr>
              <td>${z.id}</td>
              <td><c:out value="${z.nombre}"/></td>
              <td><c:out value="${z.cultivo}"/></td>
              <td><c:out value="${z.ubicacion}"/></td>
            </tr>
          </c:forEach>
        </tbody>
      </table>
    </div>
  </section>

  <section class="tarjeta">
    <h2>Registrar anotacion (RF06)</h2>
    <p class="ayuda">Los tres roles funcionales del PR09 pueden anotar observaciones sobre una zona y, si aplica,
      asociarlas al numero de una lectura.</p>
    <form method="post" action="${pageContext.request.contextPath}/anotaciones" class="formulario" id="form-anotacion">
      <div class="campo">
        <label for="zonaId">Zona *</label>
        <select id="zonaId" name="zonaId" required>
          <option value="">-- Selecciona una zona --</option>
          <c:forEach var="z" items="${zonas}">
            <option value="${z.id}" <c:if test="${formZonaId == z.id}">selected</c:if>><c:out value="${z.nombre}"/> - <c:out value="${z.cultivo}"/></option>
          </c:forEach>
        </select>
      </div>
      <div class="campo">
        <label for="autorRol">Rol que anota *</label>
        <select id="autorRol" name="autorRol" required>
          <option value="">-- Selecciona un rol --</option>
          <c:forEach var="r" items="${roles}">
            <option value="${r}" <c:if test="${formAutorRol == r}">selected</c:if>>${r}</option>
          </c:forEach>
        </select>
      </div>
      <div class="campo">
        <label for="lecturaId">Lectura relacionada (opcional, numero)</label>
        <input type="text" id="lecturaId" name="lecturaId" inputmode="numeric" maxlength="18"
               value="<c:out value='${formLecturaId}'/>">
      </div>
      <div class="campo campo-ancho">
        <label for="texto">Anotacion * (3 a 300 caracteres)</label>
        <input type="text" id="texto" name="texto" maxlength="300" value="<c:out value='${formTexto}'/>">
      </div>
      <div class="campo acciones">
        <button type="submit" id="btn-anotar">Registrar anotacion</button>
      </div>
    </form>
  </section>

  <section class="tarjeta">
    <h2>Anotaciones recientes</h2>
    <c:choose>
      <c:when test="${empty anotaciones}">
        <p class="vacio" id="sin-anotaciones">No hay anotaciones registradas.</p>
      </c:when>
      <c:otherwise>
        <div class="tabla-scroll">
          <table id="tabla-anotaciones">
            <thead><tr><th>#</th><th>Zona</th><th>Rol</th><th>Anotacion</th><th>Lectura</th><th>Creada</th></tr></thead>
            <tbody>
              <c:forEach var="n" items="${anotaciones}">
                <tr>
                  <td>${n.id}</td>
                  <td><c:out value="${n.zona}"/></td>
                  <td><span class="etiqueta etiqueta-rol"><c:out value="${n.autorRol}"/></span></td>
                  <td><c:out value="${n.texto}"/></td>
                  <td><c:if test="${n.lecturaId != null}">#${n.lecturaId}</c:if></td>
                  <td><c:out value="${n.creadaEnTexto}"/></td>
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
