// {{NOME}} — API (esqueleto da fábrica).
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
)

func rotas() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/health", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok", "sistema": "{{NOME}}"})
	})
	return mux
}

func main() {
	porta := os.Getenv("PORT")
	if porta == "" {
		porta = "8000"
	}
	log.Fatal(http.ListenAndServe(":"+porta, rotas()))
}
