import asyncio
import json
import ssl

import aiomqtt

HOST = "mqtt.hsl.fi"
TOPIC = "/hfp/v2/journey/ongoing/vp/#"


async def main():
    async with aiomqtt.Client(HOST, port=8883, tls_context=ssl.create_default_context()) as client:
        await client.subscribe(TOPIC)
        async for message in client.messages:
            vp = json.loads(message.payload)["VP"]
            print(vp["desi"], vp["oper"], vp["veh"], vp["dl"])


if __name__ == "__main__":
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
