import asyncio
import json

from ingest import KAFKA_TOPIC, forward
from tests.samples import BUS, METRO, NO_GPS


class FakeProducer:
    def __init__(self):
        self.sent = []

    async def send(self, topic, value, key=None):
        self.sent.append((topic, key, json.loads(value)))


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
