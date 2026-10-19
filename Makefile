.PHONY: install backend frontend test demo docker

install:
	python -m venv .venv
	.venv/bin/pip install -r backend/requirements.txt
	cd frontend && pnpm install

backend:
	cd backend && ../.venv/bin/uvicorn app.main:app --reload

frontend:
	cd frontend && pnpm dev

test:
	PYTHONPATH=backend .venv/bin/pytest backend/tests -q
	cd frontend && pnpm run build

demo:
	.venv/bin/python scripts/setup_demo.py

docker:
	docker compose up --build
