package models

// StreamRequest represents the incoming request for proxying a video stream
type StreamRequest struct {
	URL          string            `json:"url"`
	OriginalURL  string            `json:"original_url"`
	Quality      string            `json:"quality"`
	Language     *string           `json:"language"`
	Format       *string           `json:"format"`
	Type         *string           `json:"type"`
	Host         *string           `json:"host"`
	RequiresProxy bool             `json:"requires_proxy"`
	Headers      map[string]string `json:"headers"`
	Subtitles    []map[string]string `json:"subtitles"`
	Audios       []map[string]string `json:"audios"`
}

// StreamResponse represents the response with proxy URL
type StreamResponse struct {
	ProxyURL string `json:"proxy_url"`
	Message  string `json:"message,omitempty"`
}

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message,omitempty"`
}

