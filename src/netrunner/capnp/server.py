from __future__ import annotations

import asyncio
import logging
import socket
from dataclasses import dataclass

import capnp

logger = logging.getLogger(__name__)


@dataclass
class AsyncServer:
    bootstrap_cls: type

    @classmethod
    def connection_handler(cls, bootstrap_cls: type):
        async def new_connection(reader, writer):
            server = cls(bootstrap_cls)
            await server.myserver(reader, writer)

        return new_connection

    @classmethod
    async def run(cls, address: str, port: int, bootstrap_cls: type):
        new_connection = cls.connection_handler(bootstrap_cls)
        try:
            server = await asyncio.start_server(
                new_connection,
                address,
                port,
                family=socket.AF_INET,
            )
        except Exception:
            server = await asyncio.start_server(
                new_connection,
                address,
                port,
                family=socket.AF_INET6,
            )

        async with server:
            logger.info(f"listening on {address}:{port}...")
            await server.serve_forever()

    async def myreader(self):
        while self.retry:
            try:
                # Must be a wait_for so we don't block on read()
                data = await asyncio.wait_for(self.reader.read(4096), timeout=0.1)
            except asyncio.TimeoutError:
                logger.trace(f"{self}: myreader timeout.")
                continue
            except Exception as err:
                logger.error(f"{self}: Unknown myreader err: {err}")
                return False
            await self.server.write(data)
        logger.trace(f"{self}: myreader done.")
        return True

    async def mywriter(self):
        while self.retry:
            try:
                # Must be a wait_for so we don't block on read()
                data = await asyncio.wait_for(self.server.read(4096), timeout=0.1)
                self.writer.write(data.tobytes())
            except asyncio.TimeoutError:
                logger.trace(f"{self}: mywriter timeout.")
                continue
            except Exception as err:
                logger.error(f"{self}: Unknown mywriter err: {err}")
                return False
        logger.trace(f"{self}: mywriter done.")
        return True

    async def myserver(self, reader, writer):
        # Start TwoPartyServer using TwoWayPipe (only requires bootstrap)
        bootstrap = self.bootstrap_cls()
        self.server = capnp.TwoPartyServer(bootstrap=bootstrap)
        self.reader = reader
        self.writer = writer
        self.retry = True

        # Assemble reader and writer tasks, run in the background
        coroutines = [self.myreader(), self.mywriter()]
        tasks = asyncio.gather(*coroutines, return_exceptions=True)

        while True:
            self.server.poll_once()
            # Check to see if reader has been sent an eof (disconnect)
            if self.reader.at_eof():
                self.retry = False
                break
            await asyncio.sleep(0.01)

        # Make wait for reader/writer to finish (prevent possible resource leaks)
        await tasks

        logger.debug(f"{bootstrap.client_info.getNick()}: signed off.")
        bootstrap.close()
