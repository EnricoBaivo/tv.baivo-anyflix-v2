dev:
	uv run --env-file .env fastapi dev app/main.py --host 0.0.0.0

gen-openapi:
	uv run generate_openapi.py

lint:
	uv run ruff check .

test:
	uv run pytest

format:
	uv run ruff format .

demo-bullet-anime:
	uv run --env-file .env  demo_bullet_anime.py