import json
from typing import Dict, Any, Optional
from confluent_kafka import Message
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import os


class AvroMessageProcessor:
    """Message processor for Avro-serialized Kafka messages"""
    
    def __init__(self):
        """
        Initialize the Avro processor with Schema Registry URL
        
        Args:
            schema_registry_url: URL of the Confluent Schema Registry
        """
        # Create Schema Registry client
        schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL")
        if not schema_registry_url:
            raise ValueError("SCHEMA_REGISTRY_URL environment variable is not set")
        schema_registry_client = SchemaRegistryClient({
            'url': schema_registry_url
        })
        
        # Create Avro deserializer
        self.avro_deserializer = AvroDeserializer(schema_registry_client)
        print(f"AvroMessageProcessor initialized with Schema Registry: {schema_registry_url}")
    
    def _deserialize_key(self, msg: Message) -> Optional[Any]:
        """
        Deserialize message key, trying Avro first, then JSON, then string fallback
        
        Args:
            msg: Kafka message
            
        Returns:
            Deserialized key or None if no key
        """
        if msg.key() is None:
            return None
            
        # Try Avro deserialization first
        try:
            ctx = SerializationContext(msg.topic(), MessageField.KEY)
            return self.avro_deserializer(msg.key(), ctx)
        except Exception:
            # Avro failed, try JSON
            try:
                return json.loads(msg.key().decode('utf-8'))
            except Exception:
                # JSON failed, fallback to string
                try:
                    return msg.key().decode('utf-8')
                except Exception:
                    # Even string decoding failed, return raw bytes info
                    return f"<binary_key_length_{len(msg.key())}>"

    def __call__(self, msg: Message) -> Dict[str, Any]:
        """
        Process an Avro message by deserializing it and adding Kafka metadata
        
        Args:
            msg: Confluent Kafka message with Avro-serialized value
            
        Returns:
            Dict containing deserialized value and Kafka metadata
        """
        try:
            # Deserialize the Avro value
            ctx = SerializationContext(msg.topic(), MessageField.VALUE)
            deserialized_value = self.avro_deserializer(msg.value(), ctx)
            
            # Deserialize the key using smart detection
            deserialized_key = self._deserialize_key(msg)
            
            # Create the message structure that DLT expects
            processed_message = {
                # The actual business data (deserialized from Avro)
                **deserialized_value,
                
                # Kafka metadata (similar to DLT's default_msg_processor)
                "_kafka": {
                    "topic": msg.topic(),
                    "partition": msg.partition(), 
                    "offset": msg.offset(),
                    "timestamp": msg.timestamp()[1] if msg.timestamp()[1] >= 0 else None,
                    "key": deserialized_key,
                }
            }
            
            return processed_message
            
        except Exception as e:
            # Handle deserialization errors gracefully
            # Still try to get the key even if value deserialization failed
            fallback_key = self._deserialize_key(msg)
            
            error_message = {
                "_avro_error": str(e),
                "_raw_value_length": len(msg.value()) if msg.value() else 0,
                "_kafka": {
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset(), 
                    "timestamp": msg.timestamp()[1] if msg.timestamp()[1] >= 0 else None,
                    "key": fallback_key,
                }
            }
            
            print(f"Avro deserialization failed for {msg.topic()}[{msg.partition()}]@{msg.offset()}: {e}")
            return error_message


class JSONMessageProcessor:
    """Message processor for JSON-serialized Kafka messages"""

    def __init__(self):
        print("JSONMessageProcessor initialized")

    def _deserialize_key(self, msg: Message) -> Optional[Any]:
        """
        Deserialize message key: try JSON, fallback to UTF-8 string, then raw length
        
        Args:
            msg: Kafka message
            
        Returns:
            Deserialized key or None if key not present
        """
        if msg.key() is None:
            return None

        try:
            return json.loads(msg.key().decode("utf-8"))
        except Exception:
            try:
                return msg.key().decode("utf-8")
            except Exception:
                return f"<binary_key_length_{len(msg.key())}>"

    def __call__(self, msg: Message) -> Dict[str, Any]:
        """
        Process a JSON message and extract both content and metadata

        Args:
            msg: Confluent Kafka message with JSON-encoded value

        Returns:
            Dict with deserialized value and metadata
        """
        try:
            deserialized_value = json.loads(msg.value().decode("utf-8")) if msg.value() else {}

            deserialized_key = self._deserialize_key(msg)

            return {
                **deserialized_value,
                "_kafka": {
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                    "timestamp": msg.timestamp()[1] if msg.timestamp()[1] >= 0 else None,
                    "key": deserialized_key,
                },
            }

        except Exception as e:
            fallback_key = self._deserialize_key(msg)
            error_message = {
                "_json_error": str(e),
                "_raw_value_length": len(msg.value()) if msg.value() else 0,
                "_kafka": {
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                    "timestamp": msg.timestamp()[1] if msg.timestamp()[1] >= 0 else None,
                    "key": fallback_key,
                },
            }
            print(f"JSON deserialization failed for {msg.topic()}[{msg.partition()}]@{msg.offset()}: {e}")
            return error_message

def create_avro_processor() -> AvroMessageProcessor:
    """Factory function to create an Avro message processor"""
    return AvroMessageProcessor()

def create_json_processor() -> JSONMessageProcessor:
    return JSONMessageProcessor()

avro_processor = create_avro_processor
json_processor = create_json_processor