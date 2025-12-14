# Update API Schema Script
# Downloads the latest OpenAPI schema from the FastAPI backend and regenerates TypeScript types

$ErrorActionPreference = "Stop"

# Configuration
$BackendUrl = if ($env:BACKEND_URL) { $env:BACKEND_URL } else { "http://localhost:8000" }
$SchemaFile = "src/lib/api/openapi.json"
$TypesFile = "src/lib/api/types.d.ts"

Write-Host "🚀 Updating API schema from $BackendUrl" -ForegroundColor Cyan

# Check if backend is running
Write-Host "⏳ Checking backend connectivity..." -ForegroundColor Yellow
try {
    $null = Invoke-RestMethod -Uri "$BackendUrl/health" -Method Get -TimeoutSec 5
    Write-Host "✅ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not accessible at $BackendUrl" -ForegroundColor Red
    Write-Host "   Please start your FastAPI backend first:" -ForegroundColor Red
    Write-Host "   cd ../anyflix-backend && uv run --env-file .env fastapi dev app/main.py" -ForegroundColor Yellow
    exit 1
}

# Download the OpenAPI schema
Write-Host "📥 Downloading OpenAPI schema..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$BackendUrl/openapi.json" -Method Get -OutFile $SchemaFile
    Write-Host "✅ Schema downloaded to $SchemaFile" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to download schema" -ForegroundColor Red
    exit 1
}

# Validate the schema
Write-Host "🔍 Validating schema..." -ForegroundColor Yellow
try {
    $schema = Get-Content $SchemaFile -Raw | ConvertFrom-Json
    Write-Host "✅ Schema is valid JSON" -ForegroundColor Green
} catch {
    Write-Host "❌ Invalid JSON in schema file" -ForegroundColor Red
    exit 1
}

# Generate TypeScript types
Write-Host "🔧 Generating TypeScript types..." -ForegroundColor Yellow
try {
    npx openapi-typescript $SchemaFile -o $TypesFile
    if ($LASTEXITCODE -ne 0) { throw "npx command failed" }
    Write-Host "✅ TypeScript types generated at $TypesFile" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to generate TypeScript types" -ForegroundColor Red
    exit 1
}

# Show summary
Write-Host ""
Write-Host "🎉 API schema update complete!" -ForegroundColor Green
Write-Host "📊 Schema info:" -ForegroundColor Cyan
Write-Host "   - OpenAPI version: $($schema.openapi)"
Write-Host "   - API title: $($schema.info.title)"
Write-Host "   - API version: $($schema.info.version)"
Write-Host "   - Endpoints: $(($schema.paths.PSObject.Properties.Name).Count)"
Write-Host ""
Write-Host "🔄 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Review the generated types in $TypesFile"
Write-Host "   2. Update your components to use the new API hooks"
Write-Host "   3. Test your application with the updated schema"
Write-Host ""
Write-Host "💡 Tip: Your existing hooks in src/lib/api/hooks.ts should automatically" -ForegroundColor Yellow
Write-Host "        pick up the new types without any changes needed!" -ForegroundColor Yellow

