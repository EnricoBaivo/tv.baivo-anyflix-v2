# Proxy Setup Guide

This guide explains how to set up and use the anyflix-proxy service for video streaming.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│ Proxy Service│─────▶│ Video Host  │
│  (Player)   │      │   (Go/8081)  │      │  (External) │
└─────────────┘      └──────────────┘      └─────────────┘
```

The proxy service:
- Handles header modification for restricted video sources
- Enables CORS for cross-origin video playback
- Supports HTTP range requests for seeking
- Provides a consistent interface for all video sources

## Quick Start

### 1. Start the Proxy Service

```bash
cd anyflix-proxy
go run main.go
```

Or with Docker:
```bash
cd anyflix-proxy
docker-compose up -d
```

The proxy will start on port **8081**.

### 2. Configure the Frontend

Create a `.env.local` file in the `anyflix-player` directory:

```bash
# anyflix-player/.env.local
VITE_PROXY_URL=http://localhost:8081
```

For production, set the environment variable to your proxy service URL:
```bash
VITE_PROXY_URL=https://proxy.yourdomain.com
```

### 3. Start the Frontend

```bash
cd anyflix-player
npm run dev
```

## How It Works

### 1. Video Source with Proxy Flag

When a video source has `requires_proxy: true`, the player automatically uses the proxy:

```typescript
{
  url: "https://example.com/video.m3u8",
  original_url: "https://example.com/watch",
  quality: "1080p",
  type: "hls",
  requires_proxy: true,  // ← This triggers proxying
  headers: {
    "Referer": "https://example.com",
    "User-Agent": "Custom UA"
  }
}
```

### 2. Automatic Proxying

The `useVideoPlayer` hook automatically:
1. Detects `requires_proxy: true`
2. Sends the video source data to the proxy service
3. Receives a proxied URL
4. Uses that URL in the video player

```typescript
// In useVideoPlayer.ts
const url = await getProxiedVideoUrl(selectedVideo);
// Returns: http://localhost:8081/proxy/stream?url=...&headers=...
```

### 3. Streaming Through Proxy

The proxy service:
1. Receives the stream request
2. Applies custom headers (Referer, User-Agent, etc.)
3. Fetches the stream from the original source
4. Adds CORS headers
5. Streams the video back to the player

## API Reference

### Create Proxy URL

**Endpoint:** `POST /api/v1/proxy/create`

**Request:**
```json
{
  "url": "https://example.com/video.m3u8",
  "original_url": "https://example.com/watch",
  "quality": "1080p",
  "language": "en",
  "type": "hls",
  "requires_proxy": true,
  "headers": {
    "Referer": "https://example.com"
  }
}
```

**Response:**
```json
{
  "proxy_url": "/proxy/stream?url=...",
  "message": "Proxy URL created successfully"
}
```

### Stream Video

**Endpoint:** `GET /proxy/stream?url=<encoded_url>&headers=<encoded_json>`

Streams the actual video with modified headers.

### Health Check

**Endpoint:** `GET /api/v1/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "anyflix-proxy"
}
```

## Testing

### Test Proxy Service

```bash
# Health check
curl http://localhost:8081/api/v1/health

# Create proxy URL
curl -X POST http://localhost:8081/api/v1/proxy/create \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
    "original_url": "test",
    "quality": "720p",
    "type": "hls",
    "requires_proxy": true
  }'
```

### Test in Frontend

The frontend will automatically:
- Check if proxy is available on startup
- Use proxy for sources with `requires_proxy: true`
- Fall back to direct URLs if proxy is unavailable

## Configuration

### Environment Variables

**anyflix-proxy:**
- `PORT`: Proxy server port (default: 8081)
- `LOG_LEVEL`: Logging level (default: info)

**anyflix-player:**
- `VITE_PROXY_URL`: Proxy service URL (default: http://localhost:8081)

### Production Deployment

For production:

1. Deploy the proxy service behind a reverse proxy (nginx/caddy)
2. Enable HTTPS
3. Set appropriate CORS origins (not `*`)
4. Add rate limiting
5. Consider using Redis for session storage instead of URL params

Example nginx config:
```nginx
location /proxy/ {
    proxy_pass http://localhost:8081/proxy/;
    proxy_buffering off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Troubleshooting

### Proxy Not Available

**Error:** "Failed to get proxied URL"

**Solutions:**
1. Check if proxy service is running: `curl http://localhost:8081/api/v1/health`
2. Check frontend environment variable: `VITE_PROXY_URL`
3. Check network connectivity between frontend and proxy

### Video Not Playing

**Error:** CORS error or network error

**Solutions:**
1. Check proxy logs for errors
2. Verify the original video URL is accessible
3. Check if custom headers are correct
4. Try accessing the proxy URL directly in browser

### Seeking Not Working

**Issue:** Video doesn't seek properly

**Solutions:**
1. Verify the source supports HTTP range requests
2. Check proxy is forwarding Range headers correctly
3. Check Content-Range response headers

## Development

### Running in Development

Terminal 1 - Backend:
```bash
cd anyflix-backend
make run
```

Terminal 2 - Proxy:
```bash
cd anyflix-proxy
make run
```

Terminal 3 - Frontend:
```bash
cd anyflix-player
npm run dev
```

### Testing Changes

```bash
# Test proxy service
cd anyflix-proxy
go test ./...

# Check frontend types
cd anyflix-player
npm run build
```

## License

MIT

