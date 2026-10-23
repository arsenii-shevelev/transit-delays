import asyncio
import json

import pytest
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from testcontainers.community.kafka import KafkaContainer

from ingest import KAFKA_TOPIC, forward
from tests.samples import BUS, NO_GPS

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def bootstrap_servers():
    with KafkaContainer().with_kraft() as kafka:
        yield kafka.get_bootstrap_server()


async def payloads(*items):
    for item in items:
        yield item


async def send(bootstrap_servers, *items):
    async with AIOKafkaProducer(bootstrap_servers=bootstrap_servers) as producer:
        await forward(payloads(*items), producer)


async def read(bootstrap_servers, count):
    records = []
    async with AIOKafkaConsumer(
        KAFKA_TOPIC, bootstrap_servers=bootstrap_servers, auto_offset_reset="earliest"
    ) as consumer:
        while len(records) < count:
            records.append(await asyncio.wait_for(consumer.getone(), timeout=15))
    return records


def test_position_reaches_kafka(bootstrap_servers):
    asyncio.run(send(bootstrap_servers, NO_GPS, BUS))

    [record] = asyncio.run(read(bootstrap_servers, 1))

    assert record.key == b"22/1426"
    position = json.loads(record.value)
    assert position["line"] == "57"
    assert position["vehicle"] == 1426
    assert position["offset"] == -405
