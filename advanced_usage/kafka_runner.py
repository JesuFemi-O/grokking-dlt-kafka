import argparse
from pathlib import Path

from advanced_usage.helpers import load_config_from_yaml

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dlt_kafka_runner")

def main():
    parser = argparse.ArgumentParser(description="Run a DLT pipeline from a Kafka resource config.")
    parser.add_argument("--resource", required=True, help="The name of the Kafka resource to run")
    parser.add_argument("--destination", default="duckdb", help="DLT destination (e.g., duckdb, motherduck, snowflake)")
    parser.add_argument("--config", default=str(Path(__file__).parent.parent / "kafka.yml"), help="Path to YAML config file")

    args = parser.parse_args()

    try:
        # Load YAML config
        config_path = Path(args.config)
        resources = load_config_from_yaml(config_path)

        # Find the requested resource
        resource_config = next((r for r in resources if r.name == args.resource), None)
        if resource_config is None:
            logger.error(f"No resource found with name '{args.resource}' in {args.config}")
            sys.exit(1)

        # Create consumer, resource, and pipeline
        logger.info(f"Creating Kafka consumer for resource: {args.resource}")
        consumer = resource_config.create_consumer()

        logger.info(f"Building resource and pipeline for destination: {args.destination}")
        resource = resource_config.build_resource(consumer)
        pipeline = resource_config.build_pipeline(destination=args.destination)

        # Run the pipeline
        logger.info("Running DLT pipeline...")
        info = pipeline.run(resource, loader_file_format="parquet")
        logger.info(f"Pipeline run completed with loads IDs: {info}")
        logger.info("Pipeline execution completed successfully ✅")

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()