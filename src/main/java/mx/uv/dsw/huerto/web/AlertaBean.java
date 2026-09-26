package mx.uv.dsw.huerto.web;

import java.io.Serializable;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import javax.annotation.PostConstruct;
import javax.faces.view.ViewScoped;
import javax.inject.Named;

import mx.uv.dsw.huerto.model.Alerta;
import mx.uv.dsw.huerto.repository.LecturaRepository;

/** Consulta de alertas (RF06) con filtro y paginacion en la tabla PrimeFaces. */
@Named("alertaBean")
@ViewScoped
public class AlertaBean implements Serializable {

    private static final long serialVersionUID = 1L;
    private static final int LIMITE = 200;

    private final LecturaRepository lecturaRepository = new LecturaRepository();
    private List<Alerta> alertas = new ArrayList<>();
    private List<Alerta> alertasFiltradas;
    private boolean baseDisponible = true;

    /** f:viewAction de la vista: fuerza la creacion del bean antes del render (los mensajes de cargar() se ven). */
    public void preparar() {
        // el trabajo real lo hace @PostConstruct cargar(); aqui no hay nada mas que hacer
    }

    @PostConstruct
    public void cargar() {
        try {
            alertas = lecturaRepository.findAlertas(LIMITE);
        } catch (SQLException e) {
            baseDisponible = false;
            Mensajes.error("Base de datos no disponible", "No fue posible consultar las alertas en PostgreSQL.");
        }
    }

    public List<Alerta> getAlertas() {
        return alertas;
    }

    public List<Alerta> getAlertasFiltradas() {
        return alertasFiltradas;
    }

    public void setAlertasFiltradas(List<Alerta> alertasFiltradas) {
        this.alertasFiltradas = alertasFiltradas;
    }

    public boolean isBaseDisponible() {
        return baseDisponible;
    }
}
