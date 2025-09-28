#!/usr/bin/env python3
"""Script to generate OpenAPI JSON schema from FastAPI app."""

import json
from pathlib import Path

from app.main import app


def main():
    """Generate and save OpenAPI schema."""
    openapi_schema = app.openapi()

    # Pretty print the JSON
    openapi_json = json.dumps(openapi_schema, indent=2, ensure_ascii=False)

    # Write to file
    output_path = Path(__file__).parent / "openapi.json"
    output_path.write_text(openapi_json, encoding="utf-8")

    print(f"✅ OpenAPI schema generated successfully at: {output_path}")
    print(f"📊 Schema contains {len(openapi_schema.get('paths', {}))} endpoints")

if __name__ == "__main__":
    main()
