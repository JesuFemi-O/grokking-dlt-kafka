import time
from typing import Type

from config.settings import settings
from models import ALL_MODELS
from generators import DataGenerator, data_state
from producers import get_producer


def get_model_by_name(name: str) -> Type:
    """Get model class by name"""
    for model in ALL_MODELS:
        if model.__name__.lower() == name.lower():
            return model
    raise ValueError(f"Model '{name}' not found. Available models: {[m.__name__ for m in ALL_MODELS]}")


def delivery_report(err, msg):
    """Callback for delivery reports"""
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


def generate_data(model_name: str, count: int):
    """Generate data for a specific model"""
    print(f"🚀 Starting data generation...")
    print(f"📊 Model: {model_name}")
    print(f"📦 Count: {count}")
    print(f"🔧 Serialization: {settings.serialization_format}")
    print(f"🌐 Kafka Broker: {settings.kafka_broker}")
    
    # Get model and initialize components
    model_class = get_model_by_name(model_name)
    generator = DataGenerator()
    producer = get_producer()
    
    topic_suffix = settings.serialization_format
    topic = f"{model_class.__name__.lower()}_{topic_suffix}_topic"
    print(f"📡 Topic: {topic}")
    print()
    
    # Generate and produce data
    for i in range(count):
        try:
            # Generate instance
            instance = generator.generate_instance(model_class)
            
            # Prepare for Kafka
            instance_dict = generator.prepare_instance_for_kafka(instance)
            key = generator.generate_key(model_class, instance_dict)
            
            # Store for relationships
            generator.store_for_relationships(model_class, instance_dict)
            
            # Produce to Kafka
            producer.produce(
                model_class=model_class,
                key=key,
                value=instance_dict,
                callback=delivery_report
            )
            
            # Show progress
            if (i + 1) % 10 == 0:
                print(f"📊 Progress: {i + 1}/{count} records produced")
            
            # Small delay to avoid overwhelming
            time.sleep(settings.data_gen_delay_ms / 1000.0)
            
        except Exception as e:
            print(f"❌ Error generating record {i + 1}: {e}")
            continue
    
    # Flush producer
    producer.flush()
    print(f"🎉 Done! Generated {count} records for {model_name}")
    
    # Show relationship stats for relevant models
    if model_name.lower() in ["order", "payment", "return"]:
        print(f"📈 Relationship data summary:")
        print(f"   Orders: {len(data_state.generated_orders)}")
        print(f"   Payments: {len(data_state.generated_payments)}")


def generate_realistic_scenario(orders: int = 100, payments: int = 120, returns: int = 15):
    """Generate a realistic e-commerce scenario with related data"""
    print("🏪 Generating realistic e-commerce scenario...")
    print(f"📦 Will create {orders} orders, {payments} payments, {returns} returns")
    print(f"🔧 Serialization: {settings.serialization_format}")
    print(f"🌐 Kafka Broker: {settings.kafka_broker}")
    print()
    
    # Generate orders first
    print("1️⃣ Generating orders...")
    generate_data("order", orders)
    time.sleep(2)
    
    # Generate payments (some will reference existing orders)
    print("\n2️⃣ Generating payments...")
    generate_data("payment", payments)
    time.sleep(2)
    
    # Generate returns (will reference completed orders)
    print("\n3️⃣ Generating returns...")
    generate_data("return", returns)
    
    print("\n✨ Realistic scenario generation complete!")