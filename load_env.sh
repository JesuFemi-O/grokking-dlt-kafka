#!/bin/bash

# ----------------------------------------
# Kafka bootstrap servers
# ----------------------------------------
export BOOTSTRAP_SERVERS="localhost:29092"

# ----------------------------------------
# Schema Registry URL (for Avro support)
# ----------------------------------------
export SCHEMA_REGISTRY_URL="http://localhost:8081"

echo "✅ Environment variables set."