import os
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment-driven configuration for data generator"""
    
    # Environment
    environment: Literal["dev", "prod"] = "dev"
    
    # Kafka Configuration
    kafka_broker: str
    
    # Schema Registry Configuration  
    schema_registry_url: str
    
    # Data Generator Configuration
    serialization_format: Literal["avro", "json"] = "avro"
    data_gen_batch_size: int = 100
    data_gen_delay_ms: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()