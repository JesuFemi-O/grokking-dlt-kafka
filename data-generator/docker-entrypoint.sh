#!/bin/bash
set -e

echo "🏭 Data Generator Container Starting..."
echo "Environment: ${ENVIRONMENT:-dev}"
echo "Serialization: ${SERIALIZATION_FORMAT:-avro}"
echo "Kafka Broker: ${KAFKA_BROKER:-kafka:9092}"

# Create a simple Python connectivity checker
cat > /tmp/check_connection.py << 'EOF'
import socket
import sys

def check_connection(host, port, timeout=5):
    try:
        print(f"Attempting connection to {host}:{port}...")
        sock = socket.create_connection((host, port), timeout)
        sock.close()
        print(f"✅ Successfully connected to {host}:{port}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed for {host}: {e}")
        return False
    except socket.timeout:
        print(f"❌ Connection timeout to {host}:{port}")
        return False
    except ConnectionRefusedError:
        print(f"❌ Connection refused by {host}:{port}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error connecting to {host}:{port}: {e}")
        return False

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    success = check_connection(host, port)
    sys.exit(0 if success else 1)
EOF

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
ATTEMPT=1
while true; do
    echo "   Attempt #$ATTEMPT..."
    
    if python /tmp/check_connection.py kafka 9092; then
        break
    fi
    
    echo "   Waiting 2 seconds before retry..."
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
    
    if [ $ATTEMPT -gt 30 ]; then
        echo "❌ Gave up after 30 attempts"
        exit 1
    fi
done

# If using Avro, wait for Schema Registry
if [ "${SERIALIZATION_FORMAT:-avro}" = "avro" ]; then
    echo "⏳ Waiting for Schema Registry to be ready..."
    ATTEMPT=1
    while true; do
        echo "   Attempt #$ATTEMPT..."
        
        if python /tmp/check_connection.py schema-registry 8081; then
            break
        fi
        
        echo "   Waiting 2 seconds before retry..."
        sleep 2
        ATTEMPT=$((ATTEMPT + 1))
        
        if [ $ATTEMPT -gt 30 ]; then
            echo "❌ Gave up after 30 attempts"
            exit 1
        fi
    done
fi

echo ""
echo "🚀 Data Generator is ready to accept commands!"
echo ""
echo "Usage examples:"
echo "  docker exec data-generator python src/main.py register"
echo "  docker exec data-generator python src/main.py generate --model user --count 50"
echo "  docker exec data-generator python src/main.py scenario --orders 100"
echo "  docker exec data-generator python src/main.py list-models"
echo ""
echo "💤 Container will now sleep and wait for commands..."

# Execute the CMD or any passed arguments
exec "$@"