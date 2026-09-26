package mx.uv.dsw.huerto.web;

import java.io.Serializable;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import javax.annotation.PostConstruct;
import javax.faces.view.ViewScoped;
import javax.inject.Inject;
import javax.inject.Named;

import mx.uv.dsw.huerto.model.Anotacion;
import mx.uv.dsw.huerto.model.Zona;
import mx.uv.dsw.huerto.repository.AnotacionRepository;
import mx.uv.dsw.huerto.service.AnotacionService;
import mx.uv.dsw.huerto.service.Permisos.Permiso;
import mx.uv.dsw.huerto.service.ValidacionException;

/** Zonas y anotaciones (RF01, RF06). El rol autor se toma de la sesion, no del formulario. */
@Named("anotacionBean")
@ViewScoped
public class AnotacionBean implements Serializable {

    private static final long serialVersionUID = 1L;
    private static final int LIMITE = 200;

    @Inject
    private SesionBean sesion;

    private final AnotacionRepository repository = new AnotacionRepository();
    private final AnotacionService service = new AnotacionService(repository);

    private Long zonaId;
    private String lecturaId;
    private String texto;

    private List<Zona> zonas = new ArrayList<>();
    private List<Anotacion> anotaciones = new ArrayList<>();
    private List<Anotacion> anotacionesFiltradas;
    private boolean baseDisponible = true;

    /** f:viewAction de la vista: fuerza la creacion del bean antes del render (los mensajes de cargar() se ven). */
    public void preparar() {
        // el trabajo real lo hace @PostConstruct cargar(); aqui no hay nada mas que hacer
    }

    @PostConstruct
    public void cargar() {
        try {
            zonas = repository.findZonas();
            anotaciones = repository.findRecientes(LIMITE);
        } catch (SQLException e) {
            baseDisponible = false;
            Mensajes.error("Base de datos no disponible", "No fue posible consultar zonas y anotaciones en PostgreSQL.");
        }
    }

    public void guardar() {
        if (!sesion.puede(Permiso.ANOTAR)) {
            Mensajes.error("Accion no permitida", "Tu rol no puede registrar anotaciones.");
            return;
        }
        try {
            long id = service.registrar(zonaId == null ? null : zonaId.toString(), lecturaId, sesion.getRol(), texto);
            Mensajes.info("Anotacion #" + id + " registrada", "Firmada con el rol " + sesion.getRol() + ".");
            lecturaId = null;
            texto = null;
            anotaciones = repository.findRecientes(LIMITE);
            anotacionesFiltradas = null;
        } catch (ValidacionException e) {
            for (String err : e.getErrores()) {
                Mensajes.error("La anotacion no se registro", err);
            }
        } catch (SQLException e) {
            Mensajes.error("Error de persistencia", "PostgreSQL rechazo la operacion o no esta disponible: " + e.getMessage());
        }
    }

    public Long getZonaId() {
        return zonaId;
    }

    public void setZonaId(Long zonaId) {
        this.zonaId = zonaId;
    }

    public String getLecturaId() {
        return lecturaId;
    }

    public void setLecturaId(String lecturaId) {
        this.lecturaId = lecturaId;
    }

    public String getTexto() {
        return texto;
    }

    public void setTexto(String texto) {
        this.texto = texto;
    }

    public List<Zona> getZonas() {
        return zonas;
    }

    public List<Anotacion> getAnotaciones() {
        return anotaciones;
    }

    public List<Anotacion> getAnotacionesFiltradas() {
        return anotacionesFiltradas;
    }

    public void setAnotacionesFiltradas(List<Anotacion> anotacionesFiltradas) {
        this.anotacionesFiltradas = anotacionesFiltradas;
    }

    public boolean isBaseDisponible() {
        return baseDisponible;
    }
}
