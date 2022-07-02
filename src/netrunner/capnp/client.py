from __future__ import annotations

import asyncio
import logging
import socket
from dataclasses import dataclass

import capnp

logger = logging.getLogger(__name__)


@dataclass
class AsyncClient:
    client: object
    interface: object

    @classmethod
    async def connect(cls, address: str, port: int, bootstrap_cls: type) -> AsyncClient:
        try:
            reader, writer = await asyncio.open_connection(
                address,
                port,
                family=socket.AF_INET,
            )
        except Exception:
            reader, writer = await asyncio.open_connection(
                address,
                port,
                family=socket.AF_INET6,
            )

        logger.info(f"connected to {address}:{port}")

        # Start TwoPartyClient using TwoWayPipe (takes no arguments in this mode)
        client = capnp.TwoPartyClient()

        # Assemble reader and writer tasks, run in the background
        coroutines = [cls.myreader(client, reader), cls.mywriter(client, writer)]
        asyncio.gather(*coroutines, return_exceptions=True)

        # Bootstrap the Calculator interface
        interface = client.bootstrap().cast_as(bootstrap_cls)
        return cls(client, interface)

    @staticmethod
    async def myreader(client, reader):
        while True:
            data = await reader.read(4096)
            client.write(data)

    @staticmethod
    async def mywriter(client, writer):
        while True:
            data = await client.read(4096)
            writer.write(data.tobytes())
            await writer.drain()
