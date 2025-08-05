import re
from typing import List, Union
from confluent_kafka import Consumer


def resolve_topics_regex(consumer: Consumer, pattern: str) -> List[str]:
    """
    Resolve topic names from Kafka using a regex pattern.

    Args:
        consumer: An existing Kafka consumer
        pattern: Regex pattern to match topic names

    Returns:
        List of matched topic names
    """
    try:
        metadata = consumer.list_topics(timeout=10.0)
        all_topics = list(metadata.topics.keys())
        matched = [t for t in all_topics if re.match(pattern, t)]
        return matched
    except Exception as e:
        print(f"Failed to list topics: {e}")
        return []