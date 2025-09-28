dev:
	uv run --env-file .env fastapi dev app/main.py

gen-openapi:
	uv run generate_openapi.py

lint:
	uv run ruff check .

test:
	uv run pytest

format:
	uv run ruff format .