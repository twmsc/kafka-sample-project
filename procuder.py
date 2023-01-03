import asyncio
import json
import logging
import socket

from confluent_kafka import Producer
from aiosseclient import aiosseclient

logging.basicConfig(
    format="[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s"
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


conf = {"bootstrap.servers": "localhost:9092", "client.id": socket.gethostname()}
topic = "wikimedia.recentchange"
url = "https://stream.wikimedia.org/v2/stream/recentchange"

producer = Producer(conf)


async def async_sseclient(url):
    async for event in aiosseclient(url):
        if event.event == "message":
            try:
                change = json.loads(event.data)
            except ValueError:
                pass
            else:
                log.info("{user} edited {title}".format(**change))
                producer.produce(topic, value=event.data)


async def main():
    async_task = asyncio.create_task(async_sseclient(url))
    log.info("waiting...")

    await asyncio.sleep(5 * 60)
    async_task.cancel()

    try:
        await async_task
    except asyncio.CancelledError:
        log.info("async_task is cancelled now!")

    producer.flush()


if __name__ == "__main__":
    asyncio.run(main())
