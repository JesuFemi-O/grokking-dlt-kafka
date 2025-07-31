from datetime import datetime
from typing import Dict, Any, Type
from uuid import uuid4

from models import User, Product, Order, Payment, Return
from .fake_data import (
    generate_fake_user,
    generate_fake_product, 
    generate_fake_order,
    generate_fake_payment,
    generate_fake_return
)
from .relationships import data_state


class DataGenerator:
    """Base data generator with model routing"""
    
    # Map model names to their generator functions
    GENERATORS = {
        "user": generate_fake_user,
        "product": generate_fake_product,
        "order": generate_fake_order,
        "payment": generate_fake_payment,
        "return": generate_fake_return,
    }
    
    def generate_instance(self, model_class: Type) -> Any:
        """Generate a fake instance for the given model"""
        model_name = model_class.__name__.lower()
        
        if model_name not in self.GENERATORS:
            raise ValueError(f"No generator defined for model: {model_class.__name__}")
        
        generator_func = self.GENERATORS[model_name]
        return generator_func()
    
    def prepare_instance_for_kafka(self, instance: Any) -> Dict[str, Any]:
        """Convert instance to dict and prepare for Kafka serialization"""
        instance_dict = instance.model_dump()
        
        # Convert datetime fields to millis if present
        for k, v in instance_dict.items():
            if isinstance(v, datetime):
                instance_dict[k] = int(v.timestamp() * 1000)
        
        # Convert enum or status fields
        if "status" in instance_dict and hasattr(instance, "status"):
            instance_dict["status"] = instance.status.value if hasattr(instance.status, "value") else instance.status
        
        return instance_dict
    
    def generate_key(self, model_class: Type, instance_dict: Dict[str, Any]) -> str:
        """Generate appropriate key for Kafka message based on model type"""
        model_name = model_class.__name__.lower()
        
        if model_name == "order":
            return str(instance_dict.get("order_id"))
        elif model_name == "payment":
            return str(instance_dict.get("payment_id"))
        elif model_name == "return":
            return str(instance_dict.get("return_id"))
        elif model_name == "user":
            return str(instance_dict.get("id"))
        elif model_name == "product":
            return str(instance_dict.get("product_id"))
        else:
            return str(uuid4())
    
    def store_for_relationships(self, model_class: Type, instance_dict: Dict[str, Any]):
        """Store generated data for relationship building"""
        data_state.store_generated_data(model_class.__name__, instance_dict.copy())