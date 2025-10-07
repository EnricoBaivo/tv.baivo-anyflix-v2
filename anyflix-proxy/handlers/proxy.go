package handlers

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"time"

	"anyflix-proxy/models"
)

// ProxyHandler handles the proxy requests
type ProxyHandler struct {
	client *http.Client
}

// NewProxyHandler creates a new proxy handler
func NewProxyHandler() *ProxyHandler {
	return &ProxyHandler{
		client: &http.Client{
			Timeout: 30 * time.Second,
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				return http.ErrUseLastResponse // Don't follow redirects automatically
			},
		},
	}
}

// CreateProxyURL handles creating a proxy URL from the stream request
func (ph *ProxyHandler) CreateProxyURL(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Log incoming HTTP headers
	log.Printf("=== Incoming Request to /api/v1/proxy/create ===")
	log.Printf("Client IP: %s", r.RemoteAddr)
	log.Printf("HTTP Headers:")
	for name, values := range r.Header {
		for _, value := range values {
			log.Printf("  %s: %s", name, value)
		}
	}

	var streamReq models.StreamRequest
	if err := json.NewDecoder(r.Body).Decode(&streamReq); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request body", err)
		return
	}

	// Log stream request details
	log.Printf("Stream Request:")
	log.Printf("  URL: %s", streamReq.URL)
	log.Printf("  Original URL: %s", streamReq.OriginalURL)
	log.Printf("  Quality: %s", streamReq.Quality)
	log.Printf("  Type: %v", streamReq.Type)
	log.Printf("  Host: %v", streamReq.Host)
	log.Printf("  Requires Proxy: %v", streamReq.RequiresProxy)
	if len(streamReq.Headers) > 0 {
		log.Printf("  Custom Headers:")
		for key, value := range streamReq.Headers {
			log.Printf("    %s: %s", key, value)
		}
	}
	log.Printf("===============================================")

	// Create a proxy URL with the target URL as a query parameter
	proxyURL := fmt.Sprintf("/proxy/stream?url=%s", url.QueryEscape(streamReq.URL))

	// Store headers in query params or use a session store for production
	if len(streamReq.Headers) > 0 {
		headersJSON, _ := json.Marshal(streamReq.Headers)
		proxyURL += fmt.Sprintf("&headers=%s", url.QueryEscape(string(headersJSON)))
	}

	response := models.StreamResponse{
		ProxyURL: proxyURL,
		Message:  "Proxy URL created successfully",
	}

	respondWithJSON(w, http.StatusOK, response)
}

// ProxyStream proxies the actual video stream
func (ph *ProxyHandler) ProxyStream(w http.ResponseWriter, r *http.Request) {
	targetURL := r.URL.Query().Get("url")
	if targetURL == "" {
		respondWithError(w, http.StatusBadRequest, "Missing target URL", nil)
		return
	}

	// Log incoming stream request
	log.Printf("=== Proxying Stream Request ===")
	log.Printf("Client IP: %s", r.RemoteAddr)
	log.Printf("Method: %s", r.Method)
	log.Printf("Target URL: %s", sanitizeURL(targetURL))
	log.Printf("Incoming HTTP Headers:")
	for name, values := range r.Header {
		for _, value := range values {
			log.Printf("  %s: %s", name, value)
		}
	}

	// Parse custom headers from query params
	customHeaders := make(map[string]string)
	if headersParam := r.URL.Query().Get("headers"); headersParam != "" {
		if err := json.Unmarshal([]byte(headersParam), &customHeaders); err != nil {
			log.Printf("Failed to parse headers: %v", err)
		} else if len(customHeaders) > 0 {
			log.Printf("Custom Headers to Apply:")
			for key, value := range customHeaders {
				log.Printf("  %s: %s", key, value)
			}
		}
	}
	log.Printf("===============================")

	// Create request to the target URL
	proxyReq, err := http.NewRequest("GET", targetURL, nil)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Failed to create proxy request", err)
		return
	}

	// Copy relevant headers from original request
	ph.copyHeaders(r, proxyReq)

	// Apply custom headers (these will override any copied headers)
	for key, value := range customHeaders {
		proxyReq.Header.Set(key, value)
	}

	// Set default headers if not provided
	if proxyReq.Header.Get("User-Agent") == "" {
		proxyReq.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
	}

	// Make the request
	resp, err := ph.client.Do(proxyReq)
	if err != nil {
		respondWithError(w, http.StatusBadGateway, "Failed to fetch stream", err)
		return
	}
	defer resp.Body.Close()

	// Handle redirects manually
	if resp.StatusCode >= 300 && resp.StatusCode < 400 {
		location := resp.Header.Get("Location")
		if location != "" {
			// Create new proxy URL for the redirect
			redirectURL := fmt.Sprintf("/proxy/stream?url=%s", url.QueryEscape(location))
			if len(customHeaders) > 0 {
				headersJSON, _ := json.Marshal(customHeaders)
				redirectURL += fmt.Sprintf("&headers=%s", url.QueryEscape(string(headersJSON)))
			}
			http.Redirect(w, r, redirectURL, resp.StatusCode)
			return
		}
	}

	// Copy response headers
	ph.copyResponseHeaders(resp, w)

	// Set content type if available
	if contentType := resp.Header.Get("Content-Type"); contentType != "" {
		w.Header().Set("Content-Type", contentType)
	}

	// Set status code
	w.WriteHeader(resp.StatusCode)

	// Stream the response body
	written, err := io.Copy(w, resp.Body)
	if err != nil {
		log.Printf("Error streaming response: %v (written: %d bytes)", err, written)
		return
	}

	log.Printf("Successfully proxied stream: %d bytes from %s", written, sanitizeURL(targetURL))
}

// copyHeaders copies relevant headers from the original request
func (ph *ProxyHandler) copyHeaders(src *http.Request, dst *http.Request) {
	relevantHeaders := []string{
		"Range",
		"Accept",
		"Accept-Encoding",
		"Accept-Language",
	}

	for _, header := range relevantHeaders {
		if value := src.Header.Get(header); value != "" {
			dst.Header.Set(header, value)
		}
	}
}

// copyResponseHeaders copies relevant headers from the proxy response
func (ph *ProxyHandler) copyResponseHeaders(src *http.Response, dst http.ResponseWriter) {
	relevantHeaders := []string{
		"Content-Type",
		"Content-Length",
		"Content-Range",
		"Accept-Ranges",
		"Cache-Control",
		"ETag",
		"Last-Modified",
	}

	for _, header := range relevantHeaders {
		if value := src.Header.Get(header); value != "" {
			dst.Header().Set(header, value)
		}
	}

	// Enable CORS for video streaming
	dst.Header().Set("Access-Control-Allow-Origin", "*")
	dst.Header().Set("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
	dst.Header().Set("Access-Control-Allow-Headers", "Range, Content-Type")
	dst.Header().Set("Access-Control-Expose-Headers", "Content-Length, Content-Range, Accept-Ranges")
}

// HealthCheck handles health check requests
func (ph *ProxyHandler) HealthCheck(w http.ResponseWriter, r *http.Request) {
	response := map[string]string{
		"status":  "healthy",
		"service": "anyflix-proxy",
	}
	respondWithJSON(w, http.StatusOK, response)
}

// Helper functions
func respondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	response, _ := json.Marshal(payload)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	w.Write(response)
}

func respondWithError(w http.ResponseWriter, code int, message string, err error) {
	errResp := models.ErrorResponse{
		Error:   message,
	}
	if err != nil {
		errResp.Message = err.Error()
		log.Printf("Error: %s - %v", message, err)
	}
	respondWithJSON(w, code, errResp)
}

func sanitizeURL(rawURL string) string {
	parsed, err := url.Parse(rawURL)
	if err != nil {
		return "invalid-url"
	}
	return fmt.Sprintf("%s://%s%s", parsed.Scheme, parsed.Host, parsed.Path)
}

