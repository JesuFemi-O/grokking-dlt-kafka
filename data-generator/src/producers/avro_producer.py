import json
from typing import Dict, Any, Type

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

from config.settings import settings


class AvroProducer:
    """Producer that serializes messages to Avro using Schema Registry"""
    
    def __init__(self):
        # Initialize Schema Registry client
        schema_registry_conf = {"url": settings.schema_registry_url}
        self.schema_registry_client = SchemaRegistryClient(schema_registry_conf)
        self.producers = {}  # Cache producers by model
    
    def _get_producer(self, model_class: Type) -> SerializingProducer:
        """Get or create a producer for the given model"""
        model_name = model_class.__name__
        
        if model_name not in self.producers:
            # Generate Avro schema from model
            avro_schema_dict = model_class.avro_schema()
            avro_schema_str = json.dumps(avro_schema_dict)
            
            # Create Avro serializer
            avro_serializer = AvroSerializer(self.schema_registry_client, avro_schema_str)
            
            # Create producer configuration
            producer_conf = {
                "bootstrap.servers": settings.kafka_broker,
                "key.serializer": StringSerializer("utf_8"),
                "value.serializer": avro_serializer,
            }
            
            # Create and cache producer
            self.producers[model_name] = SerializingProducer(producer_conf)
        
        return self.producers[model_name]
    
    def produce(self, model_class: Type, key: str, value: Dict[str, Any], 
                callback=None) -> None:
        """Produce a message to Kafka"""
        producer = self._get_producer(model_class)
        topic = f"{model_class.__name__.lower()}_avro_topic"
        
        producer.produce(
            topic=topic,
            key=key,
            value=value,
            on_delivery=callback
        )
        producer.poll(0)
    
    def flush(self) -> None:
        """Flush all producers"""
        for producer in self.producers.values():
            producer.flush()
    
    def close(self) -> None:
        """Close all producers"""
        self.flush()
        # Producers don't have explicit close method, flush is sufficient