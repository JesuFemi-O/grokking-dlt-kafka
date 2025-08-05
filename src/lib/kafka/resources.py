import dlt
from contextlib import closing
from typing import Any, Callable, Dict, Iterable, List, Optional, Union, Type
from confluent_kafka import Consumer, Message, KafkaError
from dlt.common import logger
from dlt.common.typing import TDataItem, TAnyDateTime
from dlt.common.time import ensure_pendulum_datetime

from .discovery import resolve_topics_regex
from .tracking import CustomOffsetTracker
from .helpers import KafkaCredentials, default_msg_processor, OffsetTracker

@dlt.resource(
    name="kafka_messages",
    table_name=lambda msg: msg["_kafka"]["topic"],
    standalone=True,
)
def kafka_consumer(
    topics: Union[str, List[str]],
    credentials: Union[KafkaCredentials, Consumer] = dlt.secrets.value,
    msg_processor: Optional[
        Callable[[Message], Dict[str, Any]]
    ] = default_msg_processor,
    batch_size: Optional[int] = 3000,
    batch_timeout: Optional[int] = 3,
    start_from: Optional[TAnyDateTime] = None,
) -> Iterable[TDataItem]:
    """Extract recent messages from the given Kafka topics.

    The resource tracks offsets for all the topics and partitions,
    and so reads data incrementally.

    Messages from different topics are saved in different tables.

    Args:
        topics (Union[str, List[str]]): Names of topics to extract.
        credentials (Optional[Union[KafkaCredentials, Consumer]]):
            Auth credentials or an initiated Kafka consumer. By default,
            is taken from secrets.
        msg_processor(Optional[Callable]): A function-converter,
            which'll process every Kafka message after it's read and
            before it's transferred to the destination.
        batch_size (Optional[int]): Messages batch size to read at once.
        batch_timeout (Optional[int]): Maximum time to wait for a batch
            consume, in seconds.
        start_from (Optional[TAnyDateTime]): A timestamp, at which to start
            reading. Older messages are ignored.

    Yields:
        Iterable[TDataItem]: Kafka messages.
    """
    if not isinstance(topics, list):
        topics = [topics]

    if isinstance(credentials, Consumer):
        consumer = credentials
    elif isinstance(credentials, KafkaCredentials):
        consumer = credentials.init_consumer()
    else:
        raise TypeError(
            (
                "Wrong credentials type provided. Need to be of type: "
                "KafkaCredentials or confluent_kafka.Consumer"
            )
        )

    if start_from is not None:
        start_from = ensure_pendulum_datetime(start_from)

    tracker = OffsetTracker(consumer, topics, dlt.current.resource_state(), start_from)

    # read messages up to the maximum offsets,
    # not waiting for new messages
    with closing(consumer):
        while tracker.has_unread:
            messages = consumer.consume(batch_size, timeout=batch_timeout)
            if not messages:
                break

            batch = []
            for msg in messages:
                if msg.error():
                    err = msg.error()
                    if err.retriable() or not err.fatal():
                        logger.warning(f"ERROR: {err} - RETRYING")
                    else:
                        raise err
                else:
                    batch.append(msg_processor(msg))
                    tracker.renew(msg)

            yield batch

@dlt.resource(
    table_name=lambda msg: msg["_kafka"]["topic"].replace(".", "_"),
    standalone=True,
    parallelized=True
)
def enhanced_kafka_consumer(
    topics: Optional[Union[str, List[str]]] = None,
    topics_regex: Optional[str] = None,
    credentials: Union[KafkaCredentials, Consumer] = dlt.secrets.value,
    msg_processor: Optional[Callable[[Message], Dict[str, Any]]] = default_msg_processor,
    offset_tracker: OffsetTracker = CustomOffsetTracker,
    batch_size: Optional[int] = 3000,
    batch_timeout: Optional[int] = 3,
    start_from: Optional[TAnyDateTime] = None,
) -> Iterable[TDataItem]:
    """
    Enhanced Kafka consumer with advanced features:
    - Regex topic discovery
    - Custom offset tracking for dynamic topics
    - Flexible credential system (Consumer, BaseKafkaCredentials, KafkaCredentials, or dict)
    - Configurable message processors
    """

    try:
        if topics_regex:
            try:
                if isinstance(credentials, Consumer):
                    discovery_consumer = credentials
                else:
                    discovery_consumer = credentials.init_consumer()
                
                discovered_topics = resolve_topics_regex(discovery_consumer, topics_regex)

                if not discovered_topics:
                    msg = f"No topics found matching pattern: {topics_regex}"
                    logger.error(msg)
                    raise ValueError(msg)
                
                logger.info(f"Found {len(discovered_topics)} topics: {discovered_topics}")
                topics = discovered_topics

            except Exception as e:
                logger.error(f"Topic discovery failed: {e}")
                logger.info("💡 Check Kafka connection and topic permissions")
                raise
        
        elif topics is None:
            raise ValueError("You must provide either topics or topics_regex")
        
        # Ensure topics is a list
        if isinstance(topics, str):
            topics = [topics]
        
        try:
            if isinstance(credentials, Consumer):
                consumer = credentials
            elif isinstance(credentials, KafkaCredentials):
                consumer = credentials.init_consumer()
            else:
                raise TypeError("Credentials must be Consumer, BaseKafkaCredentials, KafkaCredentials, or dict")
        
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            logger.info("Check credentials and Kafka broker connectivity")
            raise

        if msg_processor is None:
            logger.warning("No message processor provided, falling back to default")
            msg_processor = default_msg_processor

        logger.info(f"Using message processor: {msg_processor.__class__.__name__}")

        if start_from is not None:
            start_from = ensure_pendulum_datetime(start_from)
            logger.info(f"Starting consumption from: {start_from}")
        
        # Use the configurable offset tracker
        try:
            tracker = offset_tracker(consumer, topics, dlt.current.resource_state(), start_from)
            logger.info("Offset tracker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize offset tracker: {e}")
            logger.info("Check topic permissions and partition access")
            raise

        with closing(consumer):
            while tracker.has_unread:
                messages = consumer.consume(batch_size, timeout=batch_timeout)
                if not messages:
                    break

                batch = []
                for msg in messages:
                    if msg.error():
                        err = msg.error()
                        if err.retriable() or not err.fatal():
                            logger.warning(f"ERROR: {err} - RETRYING")
                        else:
                            raise err
                    else:
                        batch.append(msg_processor(msg))
                        tracker.renew(msg)

                yield batch
    except Exception as e:
        logger.error(f"Enhanced Kafka consumer failed: {e}")
        raise