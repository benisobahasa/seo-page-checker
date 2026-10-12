.PHONY: install run test lint fmt docker-up

install:
	pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload

test:
	pytest -q

lint:
	ruff check .

fmt:
	ruff check --fix . && ruff format .

docker-up:
	docker compose up --build
