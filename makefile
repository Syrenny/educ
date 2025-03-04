PROJECT_CLIENT=./chat-ui
PROJECT_SERVER=chat_backend.main:app
MONGO_CONTAINER=mongo-chatui
MONGO_PORT=27017
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

.PHONY: update server mongo client benchmark-update dataset benchmark stop

# === Backend ===

## Configuring environment
update:
	uv venv
	uv pip compile requirements.in -o requirements.txt --quiet
	uv pip install -r requirements.txt --quiet

## Run FastAPI server
server: update
	uv run -m uvicorn $(PROJECT_SERVER) --reload --host $(SERVER_HOST) --port $(SERVER_PORT)

## Run MongoDB image (checks if already running)
mongo:
	@if [ -z "$$(docker ps -q -f name=$(MONGO_CONTAINER))" ]; then \
		if [ -n "$$(docker ps -aq -f name=$(MONGO_CONTAINER))" ]; then \
			docker start $(MONGO_CONTAINER); \
		else \
			docker run -d -p $(MONGO_PORT):$(MONGO_PORT) --name $(MONGO_CONTAINER) mongo:latest; \
		fi \
	fi

# === Frontend ===

## Run frontend development server
client:
	cd $(PROJECT_CLIENT) && npm install && npm run dev

# === Benchmark ===

## Configuring environment for benchmark
benchmark-update:
	uv venv
	uv pip compile ./benchmark/requirements-eval.in -o ./benchmark/requirements-eval.txt --quiet
	uv pip install -r ./benchmark/requirements-eval.txt --quiet

## Prepare dataset
dataset: benchmark-update
	uv run -m benchmark.prepare --dataset-type frames

## Run benchmark
benchmark: benchmark-update
	uv run -m benchmark.evaluate --config default-rag --benchmark frames

