import asyncio
import os
import ssl

import aiomqtt
from aiokafka import AIOKafkaProducer

from positions import parse_position

HOST = "mqtt.hsl.fi"
MQTT_TOPIC = "/hfp/v2/journey/ongoing/vp/#"
KAFKA_TOPIC = "vehicle-positions"


async def forward(payloads, producer):
    async for payload in payloads:
        position = parse_position(payload)
        if position is None:
            continue
        key = f"{position.operator}/{position.vehicle}".encode()
        await producer.send(KAFKA_TOPIC, position.model_dump_json().encode(), key=key)


async def main():
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    async with AIOKafkaProducer(bootstrap_servers=bootstrap_servers, linger_ms=100) as producer:
        async with aiomqtt.Client(HOST, port=8883, tls_context=ssl.create_default_context()) as client:
            await client.subscribe(MQTT_TOPIC)
            await forward((message.payload async for message in client.messages), producer)


if __name__ == "__main__":
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
