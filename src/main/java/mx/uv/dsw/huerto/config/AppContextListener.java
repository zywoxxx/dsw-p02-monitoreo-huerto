package mx.uv.dsw.huerto.config;

import java.sql.Driver;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Enumeration;

import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;
import javax.servlet.annotation.WebListener;

/**
 * Ciclo de vida de la aplicacion: al arrancar registra en el log si la configuracion de BD esta
 * completa; al detenerse anula el registro del driver JDBC para que Tomcat no reporte fugas de
 * memoria al re-desplegar el WAR.
 */
@WebListener
public class AppContextListener implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        sce.getServletContext().log("web1 iniciando; configuracion de BD "
            + (DbConfig.isConfigured() ? "completa" : "INCOMPLETA (faltan DB_URL/DB_USER/DB_PASSWORD)")
            + "; url=" + DbConfig.urlForDisplay());
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        ClassLoader cl = Thread.currentThread().getContextClassLoader();
        Enumeration<Driver> drivers = DriverManager.getDrivers();
        while (drivers.hasMoreElements()) {
            Driver driver = drivers.nextElement();
            if (driver.getClass().getClassLoader() == cl) {
                try {
                    DriverManager.deregisterDriver(driver);
                } catch (SQLException e) {
                    sce.getServletContext().log("No se pudo anular el registro del driver JDBC", e);
                }
            }
        }
    }
}
