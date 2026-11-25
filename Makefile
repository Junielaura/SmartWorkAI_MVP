.PHONY: init up down stop logs ps config build migrate migrate-down test shell

init:
	@test -f .env || (cp .env.example .env && sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$$(openssl rand -hex 32)|" .env && echo ".env created")

up: init
	docker compose up -d --build

down:
	docker compose down

stop:
	docker compose stop

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps

config:
	docker compose config -q && echo "compose configuration is valid"

build:
	docker compose build

migrate:
	docker compose run --rm migrate

migrate-down:
	docker compose run --rm migrate alembic downgrade -1

test:
	docker compose run --rm --no-deps backend pytest

shell:
	docker compose run --rm backend bash
