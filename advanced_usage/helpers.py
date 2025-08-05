from typing import List, Optional, Union, Callable, Dict, Any
from pydantic import BaseModel, model_validator, field_validator
from confluent_kafka import Consumer
import dlt
import os
import yaml
from pathlib import Path

from src.lib.kafka.message_processors import avro_processor, json_processor
from src.lib.kafka.tracking import CustomOffsetTracker
from src.lib.kafka.resources import enhanced_kafka_consumer

class KafkaConfig(BaseModel):
    type: str = "simple"  # 'simple' or 'msk'
    consumer_group_id: str
    topics: Optional[List[str]] = None
    topics_regex: Optional[str] = None

    @model_validator(mode="after")
    def validate_topic_choice(self) -> "KafkaConfig":
        if not self.topics and not self.topics_regex:
            raise ValueError("You must provide either 'topics' or 'topics_regex'")
        if self.topics and self.topics_regex:
            raise ValueError("You must provide only one of 'topics' or 'topics_regex', not both")
        return self
    
class ProcessingConfig(BaseModel):
    serializer: str  # 'json' or 'avro'
    target_table: Optional[str]
    batch_size: Optional[int] = 3000
    batch_timeout: Optional[int] = 3


class ResourceConfig(BaseModel):
    name: str
    kafka: KafkaConfig
    processing: ProcessingConfig

    def create_consumer(self) -> Consumer:
        """Builds a Kafka Consumer instance based on the type."""
        group_id = self.kafka.consumer_group_id
        bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS")
        if not bootstrap_servers:
            raise EnvironmentError("BOOTSTRAP_SERVERS not set")

        if self.kafka.type == "simple":
            conf = {
                "bootstrap.servers": bootstrap_servers,
                "group.id": group_id,
                "auto.offset.reset": "earliest"
            }
            return Consumer(conf)

        elif self.kafka.type == "msk":
            # assumes you define MSK oauth logic here
            raise NotImplementedError("MSK support is not implemented yet")

        else:
            raise ValueError(f"Unknown kafka type: {self.kafka.type}")
    
    def get_msg_processor(self) -> Callable[[Any], Dict[str, Any]]:
        """Selects a message processor function based on the serializer."""
        if self.processing.serializer.lower() == "json":
            return json_processor()
        elif self.processing.serializer.lower() == "avro":
            return avro_processor()
        else:
            raise ValueError(f"Unsupported serializer: {self.processing.serializer}")

    def build_resource(self, consumer: Consumer) -> Callable[[], Any]:
        """Returns a DLT resource ready to be passed to pipeline.run"""
        return (
            enhanced_kafka_consumer(
                topics=self.kafka.topics,
                topics_regex=self.kafka.topics_regex,
                credentials=consumer,
                msg_processor=self.get_msg_processor(),
                batch_size=self.processing.batch_size,
                batch_timeout=self.processing.batch_timeout,
                offset_tracker=CustomOffsetTracker
            ).with_name(self.processing.target_table or self.name)
        )

    def build_pipeline(self, destination: str = "duckdb") -> dlt.Pipeline:
        return dlt.pipeline(
            pipeline_name=f"{self.name}_{destination}",
            destination=destination,
            dataset_name=self.processing.target_table or self.name,
            progress="log"
        )

def load_config_from_yaml(path: Union[str, Path]) -> List[ResourceConfig]:
    """Load and parse resource configurations from a YAML file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"YAML config file not found: {path}")

    with path.open("r") as f:
        raw_config = yaml.safe_load(f)

    if not raw_config or "resources" not in raw_config:
        raise ValueError("Invalid config format. Expected top-level 'resources' key.")

    return [ResourceConfig(**r) for r in raw_config["resources"]]