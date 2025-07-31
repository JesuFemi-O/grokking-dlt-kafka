import json
from typing import Dict, Any, Type

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer

from config.settings import settings


class JSONProducer:
    """Producer that serializes messages to JSON (no Schema Registry)"""
    
    def __init__(self):
        # Create producer configuration
        producer_conf = {
            "bootstrap.servers": settings.kafka_broker,
        }
        
        self.producer = Producer(producer_conf)
        self.key_serializer = StringSerializer("utf_8")
    
    def produce(self, model_class: Type, key: str, value: Dict[str, Any], 
                callback=None) -> None:
        """Produce a message to Kafka"""
        topic = f"{model_class.__name__.lower()}_json_topic"
        
        # Serialize key and value
        serialized_key = self.key_serializer(key)
        serialized_value = json.dumps(value).encode('utf-8')
        
        self.producer.produce(
            topic=topic,
            key=serialized_key,
            value=serialized_value,
            on_delivery=callback
        )
        self.producer.poll(0)
    
    def flush(self) -> None:
        """Flush the producer"""
        self.producer.flush()
    
    def close(self) -> None:
        """Close the producer"""
        self.flush()