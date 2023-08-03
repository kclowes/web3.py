import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
)
from json import (
    JSONDecodeError,
)
import logging
from pathlib import (
    Path,
)
import socket
import sys
import threading
from types import (
    TracebackType,
)
from typing import (
    Any,
    Type,
    Union,
)

from web3._utils.async_caching import (
    async_lock,
)
from web3.types import (
    RPCEndpoint,
    RPCResponse,
)

from .async_base import (
    AsyncJSONBaseProvider,
)
from .ipc import (
    get_default_ipc_path,
    has_valid_json_rpc_ending,
)


async def async_get_ipc_socket(ipc_path: str, timeout: float = 2.0) -> socket.socket:
    if sys.platform == "win32":
        # On Windows named pipe is used. Simulate socket with it.
        from web3._utils.windows import (
            NamedPipe,
        )

        return NamedPipe(ipc_path)
    else:
        return await asyncio.open_unix_connection(ipc_path)


class SocketServer:
    sock = None

    def __init__(self, ipc_path):
        self.ipc_path = ipc_path

    async def __aenter__(self):
        if not self.ipc_path:
            raise FileNotFoundError(
                f"cannot connect to IPC socket at path: {self.ipc_path!r}"
            )

        if not self.sock:
            self.sock = await self._open()
        return self.sock

    async def _open(self) -> socket.socket:
        return await async_get_ipc_socket(self.ipc_path)

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_value is not None:
            try:
                reader, writer = self.sock
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print('there was an error: ', e)
            self.sock = None

_async_session_cache_lock = threading.Lock()
_async_session_pool = ThreadPoolExecutor(max_workers=1)

class AsyncIPCProvider(AsyncJSONBaseProvider):
    def __init__(
        self,
        ipc_path,
        timeout: int = 10,
        *args: Any,
        **kwargs: Any,
    ):
        self.ipc_path = ipc_path
        self._socket = SocketServer(self.ipc_path)
        super().__init__()

    async def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        json_rpc_request = self.encode_rpc_request(method, params)
        async with self._socket as sock:
            reader, writer = sock
            # try:
            writer.write(json_rpc_request)
            await writer.drain()
            # except ConnectionResetError as e:
            #     print(e)
            #     await asyncio.sleep(0)
            #     continue

            async with async_lock(_async_session_pool, _async_session_cache_lock):
                response = await reader.readline()
                return self.decode_rpc_response(response)

#####
# API
#####

# from web3 import AsyncWeb3, AsyncIPCProvider
# w3 = AsyncWeb3(AsyncIPCProvider('/path/to/file.ipc'))
# await w3.eth.get_block('latest')

# or

# from web3 import AsyncWeb3, AsyncIPCProvider
# async with AsyncWeb3(AsyncIPCProvider('/path/to/file.ipc')) as w3:
#    await w3.eth.get_block('latest')

# async def async_get_ipc_socket(ipc_path: str, timeout: float = 2.0) -> socket.socket:
#     if sys.platform == "win32":
#         # On Windows named pipe is used. Simulate socket with it.
#         from web3._utils.windows import (
#             NamedPipe,
#         )

#         return NamedPipe(ipc_path)
#     else:
#         return await asyncio.open_unix_connection(ipc_path)


# class PersistantSocket:
#     sock = None

#     def __init__(self, ipc_path: str) -> None:
#         self.ipc_path = ipc_path

#     async def __aenter__(self) -> socket.socket:
#         if not self.ipc_path:
#             raise FileNotFoundError(
#                 f"cannot connect to IPC socket at path: {self.ipc_path!r}"
#             )

#         if not self.sock:
#             self.sock = await self._open()
#         return self.sock

#     async def __aexit__(
#         self,
#         exc_type: Type[BaseException],
#         exc_value: BaseException,
#         traceback: TracebackType,
#     ) -> None:
#         # only close the socket if there was an error
#         if exc_value is not None:
#             try:
#                 self.sock.close()
#             except Exception:
#                 pass
#             self.sock = None

#     async def _open(self) -> socket.socket:
#         return await async_get_ipc_socket(self.ipc_path)

#     async def reset(self) -> socket.socket:
#         reader, writer = self.sock
#         writer.close()
#         await writer.wait_closed()
#         self.sock = await self._open()
#         return self.sock


# class AsyncIPCProvider(AsyncJSONBaseProvider):
#     logger = logging.getLogger("web3.providers.AsyncIPCProvider")
#     _socket = None

#     def __init__(
#         self,
#         ipc_path: Union[str, Path] = None,
#         timeout: int = 10,
#         *args: Any,
#         **kwargs: Any,
#     ) -> None:
#         if ipc_path is None:
#             self.ipc_path = get_default_ipc_path()
#         elif isinstance(ipc_path, str) or isinstance(ipc_path, Path):
#             self.ipc_path = str(Path(ipc_path).expanduser().resolve())
#         else:
#             raise TypeError("ipc_path must be of type string or pathlib.Path")

#         self.timeout = timeout
#         self._thread_pool = ThreadPoolExecutor(max_workers=1)
#         self._lock = async_lock(self._thread_pool, threading.Lock())
#         self._socket = PersistantSocket(self.ipc_path)
#         super().__init__()

#     def __str__(self) -> str:
#         return f"<{self.__class__.__name__} {self.ipc_path}>"

#     async def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
#         self.logger.debug(
#             f"Making request IPC. Path: {self.ipc_path}, Method: {method}"
#         )
#         request = self.encode_rpc_request(method, params)

#         # TODO - lock missing
#         async with self._socket as sock:
#             reader, writer = sock
#             try:
#                 writer.write(request)
#                 await writer.drain()
#             except BrokenPipeError:
#                 # one extra attempt, then give up
#                 sock = self._socket.reset()
#                 writer.write(request)
#                 await writer.drain()

#             raw_response = b""
#             while True:
#                 try:
#                     raw_response += await reader.read(4096)
#                 except socket.timeout:
#                     await asyncio.sleep(0)
#                     continue
#                 if raw_response == b"":
#                     await asyncio.sleep(0)
#                 elif has_valid_json_rpc_ending(raw_response):
#                     try:
#                         response = self.decode_rpc_response(raw_response)
#                     except JSONDecodeError:
#                         await asyncio.sleep(0)
#                         continue
#                     else:
#                         return response
#                 else:
#                     await asyncio.sleep(0)
#                     continue
