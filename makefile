# === Backend ===

# Configuring environment
update:
	uv venv
	uv pip compile requirements.in -o requirements.txt --quiet
	uv pip install -r requirements.txt --quiet

# Run FastAPI-server
run: update
	uv run -m uvicorn chat_backend.main:app --reload --host 0.0.0.0 --port 8000

# Run MongoDB-image
mongo:
	docker run -d -p 27017:27017 --name mongo-chatui mongo:latest


# === Benchmark ===

# Configuring environment
benchmark-update:
	uv venv
	uv pip compile ./benchmark/requirements-eval.in -o ./benchmark/requirements-eval.txt --quiet
	uv pip install -r ./benchmark/requirements-eval.txt --quiet


# Run benchmark
benchmark: benchmark-update
	uv run -m benchmark.evaluate agentic-rag
