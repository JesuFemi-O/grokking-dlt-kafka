import json
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema

from config.settings import settings
from models import ALL_MODELS


def register_schemas():
    """Register Avro schemas for all models in Schema Registry"""
    
    if settings.serialization_format != "avro":
        print("⚠️  Skipping schema registration - not using Avro serialization")
        return
    
    # Initialize Schema Registry client
    schema_registry_conf = {"url": settings.schema_registry_url}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    
    print(f"🔗 Connecting to Schema Registry at {settings.schema_registry_url}")
    
    for model in ALL_MODELS:
        try:
            # Get Avro schema dict from model
            avro_schema_dict = model.avro_schema()
            avro_schema_str = json.dumps(avro_schema_dict)
            
            # Subject name should match topic naming convention
            # Topic: {model}_avro_topic -> Subject: {model}_avro_topic-value
            subject = f"{model.__name__.lower()}_avro_topic-value"
            
            # Create Schema object
            schema_obj = Schema(avro_schema_str, "AVRO")
            
            # Register schema
            registered_id = schema_registry_client.register_schema(subject, schema_obj)
            print(f"✅ Registered schema for {model.__name__} as '{subject}' with ID {registered_id}")
            
        except Exception as e:
            print(f"❌ Failed to register schema for {model.__name__}: {e}")
    
    print("🎉 Schema registration complete!")


if __name__ == "__main__":
    register_schemas()