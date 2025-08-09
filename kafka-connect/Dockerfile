FROM debezium/connect:3.0.0.Final

# Environment variables
ENV PLUGIN_DIR=/kafka/connect/plugins
ENV WORKER_DIR=/kafka/config.orig/connect-distributed.properties
ENV CONFLUENT_CLI_INSTALL_DIR=/kafka/connect/confluent-cli
ENV PATH="$CONFLUENT_CLI_INSTALL_DIR/:$PATH"

# Package versions
ENV AVRO_CONVERTER_VERSION=7.9.0
ENV CONFLUENT_CLI_VERSION=4.9.0
ENV S3_SINK_CONNECTOR_VERSION=10.5.23


# Create neccessary directories
RUN mkdir -p $PLUGIN_DIR $CONFLUENT_CLI_INSTALL_DIR

# Install confluent-cli
RUN ARCH=$(uname -m) &&  \
    [ "$ARCH" = "aarch64" ] && ARCH="arm64"; \
    [ "$ARCH" = "x86_64" ] && ARCH="amd64"; \
    curl -L --fail -O https://packages.confluent.io/confluent-cli/archives/$CONFLUENT_CLI_VERSION/confluent_linux_$ARCH.tar.gz && \
    tar xzf confluent_linux_$ARCH.tar.gz -C /tmp/ && \
    mv /tmp/confluent/confluent $CONFLUENT_CLI_INSTALL_DIR/ && \
    rm -rf confluent_linux_$ARCH.tar.gz

# Install Confluent Plugins
RUN confluent connect plugin install --force --plugin-directory $PLUGIN_DIR --worker-configurations $WORKER_DIR confluentinc/kafka-connect-avro-converter:$AVRO_CONVERTER_VERSION && \
    confluent connect plugin install --force --plugin-directory $PLUGIN_DIR --worker-configurations $WORKER_DIR confluentinc/kafka-connect-s3:$S3_SINK_CONNECTOR_VERSION


# Restart the container
CMD ["start"]