.PHONY: help install test run docker-build docker-run clean lint format

help:
	@echo "VisionClaw Vision Service - Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make run          - Run development server"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make clean        - Clean temporary files"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

run:
	mkdir -p logs temp
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t visionclaw-vision:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env visionclaw-vision:latest

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf logs/* temp/*
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

lint:
	flake8 app tests --max-line-length=100 --extend-ignore=E203
	mypy app --ignore-missing-imports

format:
	black app tests --line-length=100
	isort app tests --profile=black
