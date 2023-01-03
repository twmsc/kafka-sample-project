# A hands-on project of Apache Kafka® event streaming application that processes real-time edits to real Wikipedia pages using Python

Goal: streams the server-sent events (SSE) from https://stream.wikimedia.org/v2/stream/recentchange to a Kafka broker and sink the data into a opensearch cluster.

## Tech stack:

- Kafka cluster management: [Confluent Platform](https://docs.confluent.io/platform/current/overview.html).
- Kafka producer: take stream data from Asynchronous Server Side Events (SSE) Client ([aiosseclient](https://github.com/ebraminio/aiosseclient)).
- Kafka consumer: consume data from Kafka broker and dump it to [opensearch](https://opensearch.org/) with bulk operation.

## Setting up the dev clusters

```shell
cd confluent-kafka && docker-compose up -d && cd ..
```

```shell
cd opensearch && docker-compose up -d && cd ..
```
