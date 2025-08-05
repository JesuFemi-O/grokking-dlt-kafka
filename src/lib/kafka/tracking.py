from confluent_kafka import Consumer, Message, TopicPartition
from confluent_kafka.admin import AdminClient, TopicMetadata
from typing import Any, Dict, List

from dlt.common import pendulum
from dlt.common.typing import DictStrAny

# Import DLT's original OffsetTracker
from .helpers import OffsetTracker

class CustomOffsetTracker(OffsetTracker):
    """
    Enhanced offset tracker that handles new topics appearing after first run
    
    Extends DLT's default OffsetTracker to support dynamic topic discovery
    by ensuring new topics are properly initialized in the state.
    """

    def __init__(
        self,
        consumer: Consumer,
        topic_names: List[str],
        pl_state: DictStrAny,
        start_from: pendulum.DateTime = None,
    ):
        # Initialize as a dict (parent's parent) to avoid calling _init_partition_offsets yet
        dict.__init__(self)

        self._consumer = consumer
        self._topics = self._read_topics(topic_names)

        # Read/init current offsets
        self._cur_offsets = pl_state.setdefault(
            "offsets", {t_name: {} for t_name in topic_names}
        )

        # Extend behavior to allow net-new topics post-first run
        self._ensure_new_topics_initialized(topic_names)

        # Now do the partition offset initialization
        self._init_partition_offsets(start_from)
    
    def _ensure_new_topics_initialized(self, topic_names: List[str]) -> None:
        """Ensure all topics have initialized offset dictionaries."""
        for t_name in topic_names:
            if t_name not in self._cur_offsets:
                self._cur_offsets[t_name] = {}
                print(f"📝 Initialized tracking for new topic: {t_name}")