.PHONY: help install dev test lint docker-up docker-down

help:
	@echo "CallSphere CRM - Make commands:"
	@echo "  make install     Install all backend and frontend dependencies"
	@echo "  make dev-backend Run FastAPI backend locally"
	@echo "  make dev-frontend Run Next.js frontend locally"
	@echo "  make test        Run backend test suite"
	@echo "  make docker-up   Start all services in Docker"
	@echo "  make docker-down Stop all Docker services"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest tests/ -v

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down -v
