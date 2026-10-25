import asyncio
import os
import ssl

import aiomqtt
from aiokafka import AIOKafkaProducer

from positions import parse_position

HOST = "mqtt.hsl.fi"
MQTT_TOPIC = "/hfp/v2/journey/ongoing/vp/#"
KAFKA_TOPIC = "vehicle-positions"
MAX_PENDING = 500


def check_deliveries(pending):
    for delivery in pending:
        if delivery.done():
            delivery.result()
    return [delivery for delivery in pending if not delivery.done()]


async def forward(payloads, producer):
    pending = []
    async for payload in payloads:
        pending = check_deliveries(pending)
        position = parse_position(payload)
        if position is None:
            continue
        key = f"{position.operator}/{position.vehicle}".encode()
        pending.append(await producer.send(KAFKA_TOPIC, position.model_dump_json().encode(), key=key))
        if len(pending) >= MAX_PENDING:
            await asyncio.gather(*pending)
            pending.clear()
    await asyncio.gather(*pending)


async def main():
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    async with AIOKafkaProducer(bootstrap_servers=bootstrap_servers, linger_ms=100) as producer:
        async with aiomqtt.Client(HOST, port=8883, tls_context=ssl.create_default_context()) as client:
            await client.subscribe(MQTT_TOPIC)
            await forward((message.payload async for message in client.messages), producer)


if __name__ == "__main__":
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
