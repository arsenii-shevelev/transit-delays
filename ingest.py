import asyncio
import ssl

import aiomqtt

from positions import parse_position

HOST = "mqtt.hsl.fi"
TOPIC = "/hfp/v2/journey/ongoing/vp/#"


async def main():
    async with aiomqtt.Client(HOST, port=8883, tls_context=ssl.create_default_context()) as client:
        await client.subscribe(TOPIC)
        async for message in client.messages:
            position = parse_position(message.payload)
            if position is None:
                continue
            print(position.line, position.vehicle, position.delay)


if __name__ == "__main__":
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
