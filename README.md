# Grokking DLT Kafka

How can dlt be used to design a micro batch etl pipeline to move data from Kafka into any of dlt's supported destination systems? That's the question I am looking to answer with this experiment.

The goal is to see what dlt supports out of the box with it's Kafka integration and then set baseline requirements for what I want to be able to do while leveraging dlt.

# Generating Dummy data for Kafka

> Before running the commands in this section you want to ensure that you have created a .env file with the contents in the .env.example file at the project root and you have spun up docker compose.

To help with this experiment, I have built a data generator with the help of Claude that can assist with Generating schema-less json serialized messages and also avro serialized messages backed by the confluent schema registry. you can explore the basic commands that can be executed using the command below:

```
#main help
docker exec -it data-generator python src/main.py --help

# Command-specific help
docker exec -it data-generator python src/main.py generate --help
docker exec -it data-generator python src/main.py scenario --help
```

by default the serialization format has been set to `avro` and so to generate data that is compatible with dlt's vanilla message processor you will need to change the serialization format via:

```
# JSON serialization (one-time)
docker exec -it -e SERIALIZATION_FORMAT=json data-generator python src/main.py generate --model user --count 10
```

Complete documentation of the data generator can be found [here](./docs/data-generator.md)

## Running the Baseline example
If we simply executed `dlt init kafka duckdb` and then installed the requirements that come with initializing the kafka source, what's the bare minimum you need to do to run a kafka pipeline?

- create your virtual env

```
uv venv .venv
```

- sync requirements

```
uv sync
```

- create your .env file

```
cp .env.example .env
```

- start docker compose

```
docker compose up -d
```

- generate some json serialized data

```
docker exec -it -e SERIALIZATION_FORMAT=json data-generator python src/main.py generate --model user --count 100
```

- load user data into duckdb

```
python dlt_kafka_baseline/simple_pipeline.py
```

- you can use the duckdb ui to query your data and see what it looks like

```
duckdb -ui
```

- let's introduce a new kafka topic

```
docker exec -it -e SERIALIZATION_FORMAT=json data-generator python src/main.py generate --model product --count 20

# add more customer data
docker exec -it -e SERIALIZATION_FORMAT=json data-generator python src/main.py generate --model user --count 50
```

- adjust topic in `dlt_kafka_baseline/simple_pipeline.py`

```python
TOPIC_NAME = ["user_json_topic", 'product_json_topic']
```

- run the pipeline again

```
python dlt_kafka_baseline/simple_pipeline.py
```

at this point you will run into an error like the one below, if you remove the new topic you just added though, the pipeline should run successfully again.

```
<class 'dlt.extract.exceptions.ResourceExtractionError'>
In processing pipe `kafka_messages`: extraction of resource `kafka_messages` in `generator` `kafka_consumer` caused an exception: 'product_json_topic'
```

so out of the box, dlt doesn't like it when you add a new topic to your pipeline after your very first run.


### Working with Avro serialized Data

what if our data was avro serialized and backed by a schema registry that tracks the schema of the data written into kafka?

- Register some subjects into the schema registry

```
docker exec -it data-generator python src/main.py register
```

- generate avro serialized data

```
docker exec -it data-generator python src/main.py generate --model user --count 25
```

- change the function that's executed in your main gaurd in `dlt_kafka_baseline/simple_pipeline.py`

```python
if __name__ == "__main__":
    # load_data_with_custom_kafka_consumer()
    load_data_from_avro_topic()
```

again, you should run into another issue

```
<class 'dlt.extract.exceptions.ResourceExtractionError'>
In processing pipe `kafka_messages`: extraction of resource `kafka_messages` in `generator` `kafka_consumer` caused an exception: 'utf-8' codec can't decode byte 0x9a in position 5: invalid start byte
```

out of the box the kafka consumer does not support processing avro serialized messages.

# What do I want in production-grade micro batch etl pipeline

- Support for regex input as topic name to allow for auto-topic discovery

- Ability to add new topic after first run

- Support for avro serialized messages

- A CLI wrapper around my dlt code 

- A yaml driven system so I can register multiple pipeline (enable self service)

I have created a [technical design document](./docs/technical-design-doc.md) to describe how I intend to build on what dlt offers out of the box to build something that meets my vision for a production-grade micro batch etl pipeline