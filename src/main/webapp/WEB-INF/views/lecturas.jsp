<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%-- Vista del flujo principal: catalogo de sensores + formulario de lectura + lecturas recientes.
     Solo presenta datos que el LecturaServlet coloca en request; no contiene SQL ni reglas. --%>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lecturas | PRxx Monitoreo de huerto</title>
  <link rel="stylesheet" href="${pageContext.request.contextPath}/css/estilos.css">
</head>
<body>
<header class="cabecera">
  <div class="contenedor">
    <h1>PRxx &middot; Monitoreo de huerto</h1>
    <p class="subtitulo">Incremento P02 &middot; JSP / Servlet 4.0 &middot; Tomcat 9 &middot; PostgreSQL 16</p>
    <nav>
      <a class="activo" href="${pageContext.request.contextPath}/lecturas">Lecturas</a>
      <a href="${pageContext.request.contextPath}/alertas">Alertas</a>
      <a href="${pageContext.request.contextPath}/health">Salud (JSON)</a>
    </nav>
  </div>
</header>

<main class="contenedor">

  <c:if test="${not empty mensajeOk}">
    <div class="aviso aviso-ok" id="aviso-ok"><c:out value="${mensajeOk}"/></div>
  </c:if>
  <c:if test="${not empty mensajeAlerta}">
    <div class="aviso aviso-alerta" id="aviso-alerta"><c:out value="${mensajeAlerta}"/></div>
  </c:if>
  <c:if test="${not empty errores}">
    <div class="aviso aviso-error" id="aviso-error">
      <strong>La lectura no se registro. Corrige lo siguiente:</strong>
      <ul>
        <c:forEach var="e" items="${errores}">
          <li><c:out value="${e}"/></li>
        </c:forEach>
      </ul>
    </div>
  </c:if>

  <section class="tarjeta">
    <h2>Registrar lectura manual</h2>
    <p class="ayuda">RF-02 / RF-03: selecciona un sensor y captura el valor medido. El sistema valida el rango
      fisico del tipo de sensor y genera una alerta si el valor sale del umbral operativo (RF-05).</p>
    <form method="post" action="${pageContext.request.contextPath}/lecturas" class="formulario" id="form-lectura">
      <div class="campo">
        <label for="sensorId">Sensor *</label>
        <select id="sensorId" name="sensorId" required>
          <option value="">-- Selecciona un sensor --</option>
          <c:forEach var="s" items="${sensores}">
            <option value="${s.id}" <c:if test="${formSensorId == s.id}">selected</c:if>><c:out value="${s.etiqueta}"/></option>
          </c:forEach>
        </select>
      </div>
      <div class="campo">
        <label for="valor">Valor medido *</label>
        <input type="text" id="valor" name="valor" inputmode="decimal" placeholder="Ej. 24.5"
               maxlength="12" value="<c:out value='${formValor}'/>">
      </div>
      <div class="campo campo-ancho">
        <label for="observacion">Observacion (opcional, max. 200)</label>
        <input type="text" id="observacion" name="observacion" maxlength="200"
               value="<c:out value='${formObservacion}'/>">
      </div>
      <div class="campo acciones">
        <button type="submit" id="btn-registrar">Registrar lectura</button>
      </div>
    </form>
  </section>

  <section class="tarjeta">
    <h2>Sensores activos (RF-01)</h2>
    <div class="tabla-scroll">
      <table id="tabla-sensores">
        <thead>
          <tr><th>Codigo</th><th>Tipo</th><th>Unidad</th><th>Zona</th><th>Huerto</th>
              <th>Rango fisico</th><th>Umbral operativo</th></tr>
        </thead>
        <tbody>
          <c:forEach var="s" items="${sensores}">
            <tr>
              <td><code><c:out value="${s.codigo}"/></code></td>
              <td><c:out value="${s.tipoNombre}"/></td>
              <td><c:out value="${s.unidad}"/></td>
              <td><c:out value="${s.zona}"/></td>
              <td><c:out value="${s.huerto}"/></td>
              <td>[<c:out value="${s.valorMinimo}"/>, <c:out value="${s.valorMaximo}"/>]</td>
              <td>
                <c:choose>
                  <c:when test="${s.conUmbral}">[<c:out value="${s.umbralMinimo}"/>, <c:out value="${s.umbralMaximo}"/>]</c:when>
                  <c:otherwise>sin umbral</c:otherwise>
                </c:choose>
              </td>
            </tr>
          </c:forEach>
        </tbody>
      </table>
    </div>
  </section>

  <section class="tarjeta">
    <h2>Lecturas recientes (RF-04)</h2>
    <c:choose>
      <c:when test="${empty lecturas}">
        <p class="vacio">Aun no hay lecturas registradas.</p>
      </c:when>
      <c:otherwise>
        <div class="tabla-scroll">
          <table id="tabla-lecturas">
            <thead>
              <tr><th>#</th><th>Sensor</th><th>Tipo</th><th>Zona</th><th>Valor</th>
                  <th>Origen</th><th>Observacion</th><th>Registrada</th><th>Alerta</th></tr>
            </thead>
            <tbody>
              <c:forEach var="l" items="${lecturas}">
                <tr class="${l.conAlerta ? 'fila-alerta' : ''}">
                  <td>${l.id}</td>
                  <td><code><c:out value="${l.sensorCodigo}"/></code></td>
                  <td><c:out value="${l.tipoNombre}"/></td>
                  <td><c:out value="${l.zona}"/></td>
                  <td class="num"><c:out value="${l.valor}"/> <c:out value="${l.unidad}"/></td>
                  <td><c:out value="${l.origen}"/></td>
                  <td><c:out value="${l.observacion}"/></td>
                  <td><c:out value="${l.registradoEnTexto}"/></td>
                  <td>
                    <c:choose>
                      <c:when test="${l.conAlerta}"><span class="etiqueta etiqueta-${l.alertaNivel}"><c:out value="${l.alertaNivel}"/></span></c:when>
                      <c:otherwise><span class="etiqueta etiqueta-ok">en rango</span></c:otherwise>
                    </c:choose>
                  </td>
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
