from confluent_kafka import Consumer, KafkaError
import dlt
from kafka import kafka_consumer

TOPIC_NAME = ["user_json_topic"] # , 'product_json_topic'
KAFKA_BROKER = "localhost:29092"
GROUP_ID = "custom-pipeline-group"


def load_data_with_custom_kafka_consumer() -> None:
    """Load data from Kafka using a custom consumer."""
    # You can choose: pass a Consumer or KafkaCredentials
    consumer_conf = {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(consumer_conf)

    pipeline = dlt.pipeline(
        pipeline_name="basic_kafka_duckdb_pipeline",
        destination='duckdb',
        dataset_name="kafka_messages",
        progress='log',
    )

    data = kafka_consumer(TOPIC_NAME, credentials=consumer)

    info = pipeline.run(data)
    print(info)


def load_data_from_avro_topic() -> None:
    """Load data from Kafka using a custom consumer."""
    # You can choose: pass a Consumer or KafkaCredentials
    consumer_conf = {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(consumer_conf)

    TOPIC_NAME = "user_avro_topic"

    pipeline = dlt.pipeline(
        pipeline_name="simple_avro_kafka_duckdb_pipeline",
        destination='duckdb',
        dataset_name="kafka_messages",
        progress='log',
    )

    data = kafka_consumer(TOPIC_NAME, credentials=consumer)

    info = pipeline.run(data)
    print(info)

if __name__ == "__main__":
    load_data_with_custom_kafka_consumer()
    # load_data_from_avro_topic()