up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

test:
	docker compose run --rm api python -m pytest

web:
	npm run dev:web

admin:
	npm run dev:admin

build:
	npm run build

test-api:
	npm run test:api
