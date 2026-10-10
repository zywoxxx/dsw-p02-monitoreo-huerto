package mx.uv.dsw.huerto.api.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;

/**
 * CORS: el navegador solo deja que el cliente Angular (otro origen, puerto 4200) llame a la API si
 * esta lo autoriza. Se permite un unico origen configurable; no se usa "*" porque viaja Authorization.
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${huerto.cors.origen}")
    private String origenPermitido;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins(origenPermitido)
            .allowedMethods("GET", "POST", "OPTIONS")
            .allowedHeaders("Authorization", "Content-Type", "Accept")
            .exposedHeaders("Location")
            .maxAge(3600);
    }

    @Bean
    public OpenAPI informacionApi() {
        return new OpenAPI().info(new Info()
            .title("PR09 Monitoreo de huerto - API REST")
            .version("0.4.0")
            .description("Generado desde el codigo. El contrato de referencia es docs/p04/openapi.yaml."));
    }
}
