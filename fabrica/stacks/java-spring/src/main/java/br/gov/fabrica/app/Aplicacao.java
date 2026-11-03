package br.gov.fabrica.app;

import java.util.Map;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class Aplicacao {
    public static void main(String[] args) { SpringApplication.run(Aplicacao.class, args); }

    @GetMapping("/api/health")
    public Map<String, String> health() { return Map.of("status", "ok", "sistema", "{{NOME}}"); }
}
