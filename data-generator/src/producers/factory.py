from typing import Union

from config.settings import settings
from .avro_producer import AvroProducer
from .json_producer import JSONProducer


class ProducerFactory:
    """Factory to create the appropriate producer based on configuration"""
    
    @staticmethod
    def create_producer() -> Union[AvroProducer, JSONProducer]:
        """Create producer based on serialization format setting"""
        if settings.serialization_format == "avro":
            return AvroProducer()
        elif settings.serialization_format == "json":
            return JSONProducer()
        else:
            raise ValueError(f"Unsupported serialization format: {settings.serialization_format}")


# Convenience function for easy import
def get_producer() -> Union[AvroProducer, JSONProducer]:
    """Get the configured producer instance"""
    return ProducerFactory.create_producer()