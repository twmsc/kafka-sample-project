import logging
import json
import time

from confluent_kafka import Consumer
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


logging.basicConfig(
    format="[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s"
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def create_opensearch_client():
    opensearch_host = "localhost"
    opensearch_port = 9200
    opensearch_auth = ("admin", "admin")

    return OpenSearch(
        hosts=[{"host": opensearch_host, "port": opensearch_port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=opensearch_auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        # ca_certs = ca_certs_path
    )


def extract_id(msg_value: dict) -> str:
    return msg_value["meta"]["id"]


def create_kafka_consumer() -> Consumer:
    conf = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "consumer-opensearch-demo",
        "auto.offset.reset": "latest",
        "enable.auto.commit": False,
    }
    topic = "wikimedia.recentchange"
    consumer = Consumer(conf)
    consumer.subscribe([topic])

    return consumer


if __name__ == "__main__":
    os_client = create_opensearch_client()

    if not os_client.indices.exists("wikimedia"):
        os_client.indices.create("wikimedia")
        log.info("The Wikimedia Index has been created!")
    else:
        log.info("The Wikimedia Index already exits!")

    consumer = create_kafka_consumer()

    try:
        while True:
            records = consumer.consume(num_messages=500, timeout=3)
            log.info(f"Received {len(records)} messages")

            if records == []:
                # Initial message consumption may take up to `session.timeout.ms` for the consumer group to
                # re-balance and start consuming
                log.info("Waiting...")

            bulk_data = []
            for msg in records:
                if msg.error():
                    log.error("ERROR: %s".format(msg.error()))

                try:
                    msg_value = json.loads(msg.value())
                    id = extract_id(msg_value)

                    # TODO: object mapping for different types of data for the same key
                    if "log_params" in msg_value:
                        msg_value.pop("log_params")

                    bulk_data.append(
                        {
                            "_op_type": "index",
                            "_index": "wikimedia",
                            "_id": id,
                            "_source": msg_value,
                        }
                    )
                except Exception as e_instance:
                    print(e_instance)

            if len(bulk_data) > 0:
                bulk(os_client, bulk_data)
                log.info(f"Inserted {len(bulk_data)} record(s).")

                try:
                    time.sleep(1)
                except InterruptedError as e:
                    log.error("ERROR: %s".format(e))

                consumer.commit(asynchronous=False)
                log.info("Offsets have been committed!\n")
    except KeyboardInterrupt:
        log.info("Interrupt from keyboard!")
    except Exception as e:
        print(e)
    finally:
        consumer.close()
        log.info("The consumer is now gracefully closed")
