package mx.uv.dsw.huerto.web;

import java.io.Serializable;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

import javax.annotation.PostConstruct;
import javax.faces.view.ViewScoped;
import javax.inject.Inject;
import javax.inject.Named;

import mx.uv.dsw.huerto.model.Lectura;
import mx.uv.dsw.huerto.model.Sensor;
import mx.uv.dsw.huerto.repository.LecturaRepository;
import mx.uv.dsw.huerto.repository.SensorRepository;
import mx.uv.dsw.huerto.service.LecturaService;
import mx.uv.dsw.huerto.service.Permisos.Permiso;
import mx.uv.dsw.huerto.service.ValidacionException;

/**
 * Flujo principal en JSF: seleccionar sensor -> capturar valor -> validar -> persistir ->
 * alerta si corresponde -> historial. Sustituye al LecturaServlet + lecturas.jsp de P02.
 *
 * El valor se recibe como texto y lo valida LecturaValidator (via LecturaService): asi una
 * entrada con tres decimales se rechaza en lugar de redondearse en un convertidor.
 */
@Named("lecturaBean")
@ViewScoped
public class LecturaBean implements Serializable {

    private static final long serialVersionUID = 1L;
    private static final int LIMITE_HISTORIAL = 200;

    @Inject
    private SesionBean sesion;

    private final SensorRepository sensorRepository = new SensorRepository();
    private final LecturaRepository lecturaRepository = new LecturaRepository();
    private final LecturaService lecturaService = new LecturaService(sensorRepository, lecturaRepository);

    // formulario
    private Long sensorId;
    private String valor;
    private String observacion;

    // datos de la vista
    private List<Sensor> sensores = new ArrayList<>();
    private List<Lectura> lecturas = new ArrayList<>();
    private List<Lectura> lecturasFiltradas;
    private boolean baseDisponible = true;

    /** f:viewAction de la vista: fuerza la creacion del bean antes del render (los mensajes de cargar() se ven). */
    public void preparar() {
        // el trabajo real lo hace @PostConstruct cargar(); aqui no hay nada mas que hacer
    }

    @PostConstruct
    public void cargar() {
        try {
            sensores = sensorRepository.findActivos();
            lecturas = lecturaRepository.findRecientes(LIMITE_HISTORIAL);
            baseDisponible = true;
        } catch (SQLException e) {
            baseDisponible = false;
            Mensajes.error("Base de datos no disponible",
                "No fue posible consultar PostgreSQL. Verifica el servicio y las variables DB_* de Tomcat.");
        }
    }

    /** Accion del boton Registrar (AJAX). Devuelve null para quedarse en la vista y conservar lo capturado. */
    public void guardar() {
        if (!sesion.puede(Permiso.REGISTRAR_LECTURA)) {
            Mensajes.error("Accion no permitida", "Tu rol (" + sesion.getRol() + ") solo puede consultar lecturas.");
            return;
        }
        try {
            LecturaService.Resultado r = lecturaService.registrar(
                sensorId == null ? null : sensorId.toString(), valor, observacion);
            Mensajes.info("Lectura #" + r.getLecturaId() + " registrada",
                "Se guardo con procedencia manual y su instante de captura.");
            if (r.getAlertaNivel() != null) {
                Mensajes.advertencia("Alerta " + r.getAlertaNivel() + " generada",
                    "El valor esta fuera del umbral operativo del sensor; la alerta quedo en la misma transaccion.");
            }
            // solo se limpia el formulario cuando la persistencia se confirmo
            valor = null;
            observacion = null;
            lecturas = lecturaRepository.findRecientes(LIMITE_HISTORIAL);
            lecturasFiltradas = null;
        } catch (ValidacionException e) {
            for (String err : e.getErrores()) {
                Mensajes.error("La lectura no se registro", err);
            }
        } catch (SQLException e) {
            Mensajes.error("Error de persistencia", "PostgreSQL rechazo la operacion o no esta disponible: " + e.getMessage());
        }
    }

    /** Sensor elegido en el selector, para mostrar unidad, rango fisico y umbral antes de capturar. */
    public Sensor getSensorSeleccionado() {
        if (sensorId == null) {
            return null;
        }
        return sensores.stream().filter(s -> Objects.equals(s.getId(), sensorId)).findFirst().orElse(null);
    }

    public List<String> getZonas() {
        return sensores.stream().map(Sensor::getZona).distinct().sorted().collect(Collectors.toList());
    }

    public List<String> getVariables() {
        return sensores.stream().map(Sensor::getVariableNombre).distinct().sorted().collect(Collectors.toList());
    }

    public Long getSensorId() {
        return sensorId;
    }

    public void setSensorId(Long sensorId) {
        this.sensorId = sensorId;
    }

    public String getValor() {
        return valor;
    }

    public void setValor(String valor) {
        this.valor = valor;
    }

    public String getObservacion() {
        return observacion;
    }

    public void setObservacion(String observacion) {
        this.observacion = observacion;
    }

    public List<Sensor> getSensores() {
        return sensores;
    }

    public List<Lectura> getLecturas() {
        return lecturas;
    }

    public List<Lectura> getLecturasFiltradas() {
        return lecturasFiltradas;
    }

    public void setLecturasFiltradas(List<Lectura> lecturasFiltradas) {
        this.lecturasFiltradas = lecturasFiltradas;
    }

    public boolean isBaseDisponible() {
        return baseDisponible;
    }
}
