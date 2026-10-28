"""
diagrama_docker.py - Dibuja docs/p05/diagramas/05_docker_nginx.png: los tres contenedores del PR09 sobre la red
Docker "huerto" con nginx como unica entrada. Reutiliza los trazos de diagramas_p04.py. Requiere Pillow.
"""
from pathlib import Path

from diagramas_p04 import (AMBAR, AZUL, BLANCO, F_CAJA, F_MIN, F_MINB, F_MONO, GRIS, GRIS_CLARO, GRIS_MEDIO,
                           VERDE, VERDE_CLARO, caja, capa, etiqueta, flecha, lienzo)

OUT = Path(__file__).resolve().parent.parent / "docs" / "p05" / "diagramas"
OUT.mkdir(parents=True, exist_ok=True)


def docker_nginx():
    img, d = lienzo(1900, 980, "Despliegue en Docker: PostgreSQL, API y cliente detras de nginx",
                    "docker compose -f docker/docker-compose.yml --profile app up -d --build. Red Docker \"huerto\"; solo nginx publica un puerto.")
    n0 = caja(d, 60, 300, 300, "Navegador", ["http://localhost", "(WEB_PORT, 80 por omision)", "token en sessionStorage"], GRIS_MEDIO, BLANCO)
    capa(d, 440, 100, 1420, 760, "Red Docker \"huerto\"  (docker/docker-compose.yml, proyecto dsw-p02-huerto)",
         "Los tres contenedores se resuelven por nombre de servicio: web, api, db", VERDE)
    w = caja(d, 480, 200, 420, "web  -  dsw-p02-huerto-web", ["imagen huerto-web:0.5.0", "nginx:1.27-alpine", "estaticos de Angular (ng build)",
                                                             "nginx.conf:", "  /        -> index.html (SPA)", "  /api/    -> http://api:8081/api/",
                                                             "  swagger  -> http://api:8081"], AZUL, BLANCO)
    a = caja(d, 980, 200, 400, "api  -  dsw-p02-huerto-api", ["imagen huerto-api:0.5.0", "eclipse-temurin:11-jre-alpine", "usuario sin privilegios",
                                                            "puerto 8081 solo en la red", "DB_URL=jdbc:postgresql://db:5432/...", "JWT_SECRET, CORS_ORIGIN",
                                                            "healthcheck: /api/health"], VERDE, BLANCO)
    b = caja(d, 1460, 200, 360, "db  -  dsw-p02-huerto-db", ["imagen postgres:16", "volumen pgdata (se conserva)", "sql/01 y 02 al crear el volumen",
                                                           "5432 en la red; 5436 al equipo", "   solo para psql y scripts", "healthcheck: pg_isready"], AMBAR, BLANCO)
    y = 330
    flecha(d, (n0[2], y), (w[0], y), GRIS, 3, doble=True)
    etiqueta(d, 368, y - 50, ["HTTP :80"], GRIS, BLANCO, F_MINB, GRIS_MEDIO)
    flecha(d, (w[2], y), (a[0], y), GRIS, 3, doble=True)
    etiqueta(d, 912, y - 50, ["proxy", "/api"], GRIS, BLANCO, F_MINB, GRIS_MEDIO)
    flecha(d, (a[2], y), (b[0], y), GRIS, 3, doble=True)
    etiqueta(d, 1392, y - 50, ["JDBC"], GRIS, BLANCO, F_MINB, GRIS_MEDIO)
    d.rectangle([480, 520, 1820, 700], fill=BLANCO, outline=GRIS_MEDIO)
    d.text((496, 530), "Orden de arranque y salud", font=F_CAJA, fill=GRIS)
    for i, l in enumerate(["1. db arranca; pg_isready cada 5 s hasta que acepta conexiones.",
                           "2. api arranca cuando db esta sana; wget a /api/health cada 10 s (503 mientras no llegue a la base).",
                           "3. web arranca cuando api esta sana; nginx responde en el puerto 80 del contenedor y WEB_PORT del equipo.",
                           "Ni api ni db publican puertos al equipo: todo entra por nginx. Sin --profile app solo se levanta db (P02 a P05).",
                           "El cliente usa rutas relativas (/api), asi que no cambia nada entre ng serve con proxy y nginx."]):
        d.text((496, 562 + 24 * i), l, font=F_MIN, fill=GRIS)
    d.rectangle([480, 730, 1820, 840], fill=VERDE_CLARO, outline=VERDE, width=2)
    d.text((496, 740), "Imagenes en dos etapas (multi-stage)", font=F_CAJA, fill=VERDE)
    d.text((496, 770), "api-spring/Dockerfile:      maven:3.9.9-eclipse-temurin-11 compila  ->  eclipse-temurin:11-jre-alpine solo con el jar", font=F_MONO, fill=GRIS)
    d.text((496, 796), "frontend-angular/Dockerfile: node:18.20-alpine compila (ng build)  ->  nginx:1.27-alpine solo con los estaticos", font=F_MONO, fill=GRIS)
    d.text((60, 900), "Datos ficticios de laboratorio; credenciales en docker/.env (no versionado). No se usa infraestructura de terceros.", font=F_MIN, fill=GRIS_MEDIO)
    img.save(OUT / "05_docker_nginx.png")


if __name__ == "__main__":
    docker_nginx()
    print("Diagrama en", OUT.relative_to(OUT.parent.parent.parent))
