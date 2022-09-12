# Patterned after: https://github.com/fokko/docker-druid/
FROM openjdk:11

# we need Python2 to run the indexing scripts
# Druid issue to upgrade to python3 https://github.com/apache/druid/issues/12824
RUN apt update && apt install -y python2

ARG DRUID_VERSION=0.22.1
ARG ZOOKEEPER_VERSION=3.6.3
ENV DRUID_SKIP_JAVA_CHECK=1

# Get Druid
RUN mkdir -p /tmp \
    && cd /tmp/ \
    && curl -fsLS "https://archive.apache.org/dist/druid/$DRUID_VERSION/apache-druid-$DRUID_VERSION-bin.tar.gz" | tar xvz \
    && mv apache-druid-$DRUID_VERSION /opt/druid

WORKDIR /opt/druid/

# Zookeeper
RUN curl -fsLS "https://dlcdn.apache.org/zookeeper/zookeeper-$ZOOKEEPER_VERSION/apache-zookeeper-$ZOOKEEPER_VERSION.tar.gz" | tar xvz \
    && mv apache-zookeeper-$ZOOKEEPER_VERSION zk

COPY common.runtime.properties conf/druid/single-server/micro-quickstart/_common/

# Expose ports:
# - 8888: HTTP (router)
# - 8081: HTTP (coordinator)
# - 8082: HTTP (broker)
# - 8083: HTTP (historical)
# - 8090: HTTP (overlord)
# - 2181 2888 3888: ZooKeeper
EXPOSE 8888
EXPOSE 8081
EXPOSE 8082
EXPOSE 8083
EXPOSE 8090
EXPOSE 2181 2888 3888

ENTRYPOINT ./bin/start-micro-quickstart