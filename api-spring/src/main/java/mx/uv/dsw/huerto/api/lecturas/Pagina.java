package mx.uv.dsw.huerto.api.lecturas;

import java.util.List;

/** Respuesta paginada (esquema "PaginaLecturas" del contrato). */
public class Pagina<T> {

    private final List<T> contenido;
    private final int pagina;
    private final int tamano;
    private final long total;

    public Pagina(List<T> contenido, int pagina, int tamano, long total) {
        this.contenido = contenido;
        this.pagina = pagina;
        this.tamano = tamano;
        this.total = total;
    }

    public List<T> getContenido() {
        return contenido;
    }

    public int getPagina() {
        return pagina;
    }

    public int getTamano() {
        return tamano;
    }

    public long getTotal() {
        return total;
    }
}
