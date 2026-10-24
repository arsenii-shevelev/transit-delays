import asyncio
import json

import pytest
from aiokafka.errors import KafkaTimeoutError

from ingest import KAFKA_TOPIC, forward
from tests.samples import BUS, METRO, NO_GPS


class FakeProducer:
    def __init__(self, error=None):
        self.sent = []
        self.error = error

    async def send(self, topic, value, key=None):
        self.sent.append((topic, key, json.loads(value)))
        delivery = asyncio.get_running_loop().create_future()
        if self.error:
            delivery.set_exception(self.error)
        else:
            delivery.set_result(None)
        return delivery


async def payloads(*items):
    for item in items:
        yield item


def test_sends_parsed_position_keyed_by_vehicle():
    producer = FakeProducer()

    asyncio.run(forward(payloads(BUS), producer))

    topic, key, value = producer.sent[0]
    assert topic == KAFKA_TOPIC
    assert key == b"22/1426"
    assert value["line"] == "57"
    assert value["offset"] == -405


def test_skips_messages_it_cannot_parse():
    producer = FakeProducer()

    asyncio.run(forward(payloads(NO_GPS, METRO, b"not json", BUS), producer))

    assert len(producer.sent) == 1


def test_fails_when_kafka_does_not_accept_a_position():
    producer = FakeProducer(error=KafkaTimeoutError())

    with pytest.raises(KafkaTimeoutError):
        asyncio.run(forward(payloads(BUS), producer))
