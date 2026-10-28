# API REST del PR09 (Spring Boot 2.7, Java 11). Dos etapas: Maven compila y empaqueta; la imagen final
# solo lleva el JRE y el jar. Se construye desde la raiz del repositorio:
#   docker build -f api-spring/Dockerfile -t huerto-api .
FROM maven:3.9.9-eclipse-temurin-11 AS build
WORKDIR /src
# Primero el pom para que las dependencias queden en cache mientras no cambie
COPY api-spring/pom.xml .
RUN mvn -B -q dependency:go-offline
COPY api-spring/src ./src
RUN mvn -B -q -DskipTests clean package

FROM eclipse-temurin:11-jre-alpine
RUN addgroup -S huerto && adduser -S -G huerto huerto
WORKDIR /app
COPY --from=build /src/target/api-spring.jar app.jar
USER huerto
EXPOSE 8081
# wget viene con busybox en alpine; /api/health responde 503 si PostgreSQL no esta
HEALTHCHECK --interval=10s --timeout=5s --start-period=40s --retries=5 \
  CMD wget -q -O /dev/null http://localhost:8081/api/health || exit 1
ENTRYPOINT ["java", "-jar", "app.jar"]
