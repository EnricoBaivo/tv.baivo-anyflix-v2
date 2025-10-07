.PHONY: build run clean docker-build docker-run test deps

# Build the application
build:
	go build -o anyflix-proxy .

# Run the application
run:
	go run main.go

# Clean build artifacts
clean:
	rm -f anyflix-proxy
	go clean

# Install dependencies
deps:
	go mod download
	go mod tidy

# Build Docker image
docker-build:
	docker build -t anyflix-proxy:latest .

# Run with Docker Compose
docker-run:
	docker-compose up -d

# Stop Docker containers
docker-stop:
	docker-compose down

# View Docker logs
docker-logs:
	docker-compose logs -f

# Test the application
test:
	go test -v ./...

# Run with hot reload (requires air)
dev:
	air

# Format code
fmt:
	go fmt ./...

# Lint code (requires golangci-lint)
lint:
	golangci-lint run

# Show help
help:
	@echo "Available targets:"
	@echo "  build        - Build the application"
	@echo "  run          - Run the application"
	@echo "  clean        - Clean build artifacts"
	@echo "  deps         - Install dependencies"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker containers"
	@echo "  docker-logs  - View Docker logs"
	@echo "  test         - Run tests"
	@echo "  dev          - Run with hot reload"
	@echo "  fmt          - Format code"
	@echo "  lint         - Lint code"

