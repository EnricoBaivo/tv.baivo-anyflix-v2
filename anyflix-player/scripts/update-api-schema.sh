#!/bin/bash

# Update API Schema Script
# Downloads the latest OpenAPI schema from the FastAPI backend and regenerates TypeScript types

set -e

# Configuration
BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
SCHEMA_FILE="src/lib/api/openapi.json"
TYPES_FILE="src/lib/api/types.d.ts"

echo "🚀 Updating API schema from $BACKEND_URL"

# Check if backend is running
echo "⏳ Checking backend connectivity..."
if ! curl -s --fail "$BACKEND_URL/health" > /dev/null; then
    echo "❌ Backend not accessible at $BACKEND_URL"
    echo "   Please start your FastAPI backend first:"
    echo "   cd ../anyflix-backend && uv run --env-file .env fastapi dev app/main.py"
    exit 1
fi

echo "✅ Backend is running"

# Download the OpenAPI schema
echo "📥 Downloading OpenAPI schema..."
if curl -s --fail "$BACKEND_URL/openapi.json" -o "$SCHEMA_FILE"; then
    echo "✅ Schema downloaded to $SCHEMA_FILE"
else
    echo "❌ Failed to download schema"
    exit 1
fi

# Validate the schema
echo "🔍 Validating schema..."
if ! python3 -m json.tool "$SCHEMA_FILE" > /dev/null; then
    echo "❌ Invalid JSON in schema file"
    exit 1
fi

echo "✅ Schema is valid JSON"

# Generate TypeScript types
echo "🔧 Generating TypeScript types..."
if npx openapi-typescript "$SCHEMA_FILE" -o "$TYPES_FILE"; then
    echo "✅ TypeScript types generated at $TYPES_FILE"
else
    echo "❌ Failed to generate TypeScript types"
    exit 1
fi

# Show summary
echo ""
echo "🎉 API schema update complete!"
echo "📊 Schema info:"
echo "   - OpenAPI version: $(jq -r '.openapi' "$SCHEMA_FILE")"
echo "   - API title: $(jq -r '.info.title' "$SCHEMA_FILE")"
echo "   - API version: $(jq -r '.info.version' "$SCHEMA_FILE")"
echo "   - Endpoints: $(jq -r '.paths | keys | length' "$SCHEMA_FILE")"
echo ""
echo "🔄 Next steps:"
echo "   1. Review the generated types in $TYPES_FILE"
echo "   2. Update your components to use the new API hooks"
echo "   3. Test your application with the updated schema"
echo ""
echo "💡 Tip: Your existing hooks in src/lib/api/hooks.ts should automatically"
echo "        pick up the new types without any changes needed!"
