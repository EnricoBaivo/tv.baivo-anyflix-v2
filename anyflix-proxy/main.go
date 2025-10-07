package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"anyflix-proxy/handlers"

	"github.com/gorilla/mux"
	"github.com/rs/cors"
)

func main() {
	// Get port from environment or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "8081"
	}

	// Initialize handlers
	proxyHandler := handlers.NewProxyHandler()

	// Setup router
	router := mux.NewRouter()

	// API routes
	api := router.PathPrefix("/api/v1").Subrouter()
	api.HandleFunc("/health", proxyHandler.HealthCheck).Methods("GET")
	api.HandleFunc("/proxy/create", proxyHandler.CreateProxyURL).Methods("POST")
	
	// Proxy routes (direct streaming)
	router.HandleFunc("/proxy/stream", proxyHandler.ProxyStream).Methods("GET", "HEAD")

	// CORS setup
	c := cors.New(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "HEAD", "OPTIONS"},
		AllowedHeaders:   []string{"*"},
		ExposedHeaders:   []string{"Content-Length", "Content-Range", "Accept-Ranges"},
		AllowCredentials: false,
		MaxAge:           300,
	})

	// Wrap router with CORS
	handler := c.Handler(router)

	// Setup server
	srv := &http.Server{
		Handler:      handler,
		Addr:         "0.0.0.0:" + port,
		WriteTimeout: 60 * time.Second,
		ReadTimeout:  60 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	log.Printf("Starting anyflix-proxy server on port %s", port)
	log.Printf("Health check: http://localhost:%s/api/v1/health", port)
	log.Printf("Create proxy: POST http://localhost:%s/api/v1/proxy/create", port)
	log.Printf("Stream proxy: GET http://localhost:%s/proxy/stream?url=<encoded_url>", port)
	
	if err := srv.ListenAndServe(); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

