package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"anyflix-proxy/models"
)

func TestHealthCheck(t *testing.T) {
	handler := NewProxyHandler()
	req, err := http.NewRequest("GET", "/api/v1/health", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handlerFunc := http.HandlerFunc(handler.HealthCheck)
	handlerFunc.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	var response map[string]string
	if err := json.Unmarshal(rr.Body.Bytes(), &response); err != nil {
		t.Errorf("Failed to parse response: %v", err)
	}

	if response["status"] != "healthy" {
		t.Errorf("Expected status to be 'healthy', got '%s'", response["status"])
	}
}

func TestCreateProxyURL(t *testing.T) {
	handler := NewProxyHandler()

	streamReq := models.StreamRequest{
		URL:          "https://example.com/video.m3u8",
		OriginalURL:  "https://example.com/watch",
		Quality:      "1080p",
		RequiresProxy: true,
		Headers: map[string]string{
			"Referer": "https://example.com",
		},
	}

	body, _ := json.Marshal(streamReq)
	req, err := http.NewRequest("POST", "/api/v1/proxy/create", bytes.NewBuffer(body))
	if err != nil {
		t.Fatal(err)
	}
	req.Header.Set("Content-Type", "application/json")

	rr := httptest.NewRecorder()
	handlerFunc := http.HandlerFunc(handler.CreateProxyURL)
	handlerFunc.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	var response models.StreamResponse
	if err := json.Unmarshal(rr.Body.Bytes(), &response); err != nil {
		t.Errorf("Failed to parse response: %v", err)
	}

	if response.ProxyURL == "" {
		t.Error("Expected proxy URL to be generated")
	}
}

func TestCreateProxyURLInvalidMethod(t *testing.T) {
	handler := NewProxyHandler()
	req, err := http.NewRequest("GET", "/api/v1/proxy/create", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handlerFunc := http.HandlerFunc(handler.CreateProxyURL)
	handlerFunc.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusMethodNotAllowed {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusMethodNotAllowed)
	}
}

func TestProxyStreamMissingURL(t *testing.T) {
	handler := NewProxyHandler()
	req, err := http.NewRequest("GET", "/proxy/stream", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handlerFunc := http.HandlerFunc(handler.ProxyStream)
	handlerFunc.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusBadRequest {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusBadRequest)
	}
}

