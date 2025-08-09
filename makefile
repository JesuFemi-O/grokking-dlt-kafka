.PHONY: build-connect up down logs

# Kafka Connect URL
CONNECT_URL ?= http://localhost:8083

build-connect:
	docker buildx build --platform linux/amd64 -t dlt/kafka-connect:latest ./kafka-connect --load

up:
	docker compose up -d

down:
	docker compose down -v

# Create the Debezium connector from src.json
deploy-connector:
	@echo "Creating connector from ./kafka-connect/connector/src.json..."
	curl -sS -X POST $(CONNECT_URL)/connectors \
		-H "Content-Type: application/json" \
		-d @./kafka-connect/connector/src.json
	@echo "\nCreation request sent."