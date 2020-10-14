# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 20th 2020

Modified By: hsky77
Last Updated: October 1st 2020 21:53:41 pm
'''

import os
import math
import asyncio
import cgi
import re
from typing import Any, Dict, Union

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, stream_request_body
from tornado.websocket import WebSocketHandler

from .mixin import TornadoMixin

from ....util import join_path, FunctionQueueWorker
from ...constants import GB, KB, LocalCode_Missing_Required_Parameter, LocalCode_Upload_Success


class RequestController(TornadoMixin, RequestHandler):
    """base http request hanlder class of hyssop"""

    def set_default_headers(self):
        self.set_header('App-Name', self.application_name)


class WebSocketController(TornadoMixin, WebSocketHandler):
    """base web socket hanlder class of hyssop"""

    def __init__(self, application, request, **kwds):
        super().__init__(application, request, **kwds)
        self.io_loop = IOLoop.current(False)

    def set_default_headers(self):
        self.set_header('App-Name', self.application_name)

    def write_message(self, message: Union[bytes, str, Dict[str, Any]], binary: bool = False) -> 'Future[None]':
        if IOLoop.current(False) is self.io_loop:
            try:
                return super().write_message(message, binary)
            except IOError:
                self.io_loop.add_callback(self.on_close)
        else:
            self.io_loop.add_callback(self.write, message, binary)


class StreamingDownloadController(RequestController):
    SUPPORTED_METHODS = ("GET", "OPTIONS")

    def initialize(self, chunk_size: int = 4*KB, **kwds):
        self.chunk_size = chunk_size

    async def _prepare_binary(self):
        raise NotImplementedError()

    async def get(self):
        bdata = await self._prepare_binary()
        self.set_header('Content-Type', 'application/octet-stream')

        for i in range(0, math.ceil(len(bdata) / self.chunk_size)):
            start = i * self.chunk_size
            data = bdata[start:min(start+self.chunk_size, len(bdata))]
            self.write(data)
            await asyncio.sleep(0)

        self.finish()


@stream_request_body
class StreamingUploadController(RequestController):
    SUPPORTED_METHODS = ("POST", "PUT", "OPTIONS")

    def initialize(self, upload_dir: str = '', max_stream_size: int = 1*GB,  **kwds):
        self.upload_dir = join_path(self.root_dir, upload_dir)
        self.request.connection.set_max_body_size(max_stream_size)

        self._data_worker = FunctionQueueWorker()
        self.content_mime_type, self.content_mime_options = cgi.parse_header(
            self.request.headers['Content-Type'])

        self.bytes_length = 0

    async def prepare(self):
        pass

    async def data_received(self, chunk):
        self.bytes_length = self.bytes_length + len(chunk)
        self._data_worker.run_method(
            self._on_chunk_received, self.request.headers, chunk, self.bytes_length)

    async def post(self):
        while not self._data_worker.pending_count == 0:
            await asyncio.sleep(0)
        self._data_worker.dispose()

        with self.component_executor.get_executor() as executor:
            await executor.run_method_async(self._on_data_received, self.request.headers, self.bytes_length)

    async def put(self):
        while not self._data_worker.pending_count == 0:
            await asyncio.sleep(0)
        self._data_worker.dispose()

        with self.component_executor.get_executor() as executor:
            await executor.run_method_async(self._on_data_received, self.request.headers, self.bytes_length)

    def _on_chunk_received(self, headers, chunk, bytes_size_received):
        raise NotImplementedError()

    def _on_data_received(self, headers, bytes_size_received):
        pass

    def _handle_request_exception(self, e: BaseException) -> None:
        self._data_worker.dispose()
        super()._handle_request_exception(e)


class StreamingFileUploadController(StreamingUploadController):
    async def prepare(self):
        await super().prepare()
        self.filename = self.request.headers.get("filename")
        if self.filename is None:
            raise KeyError(self.component_localization.get_message(
                LocalCode_Missing_Required_Parameter, 'filename'))

        path = join_path(self.upload_dir, self.filename)

        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        self.__file = open(path, 'wb')

    def _on_chunk_received(self, headers, chunk, bytes_size_received):
        if self.__file is not None:
            self.__file.write(chunk)

    def _on_data_received(self, headers, bytes_size_received):
        if self.__file is not None:
            self.__file.close()
            self.__file = None

            self.log_info(self.component_localization.get_message(
                LocalCode_Upload_Success, self.filename))
            self.write(self.component_localization.get_message(
                LocalCode_Upload_Success, self.filename))


class ReservedProxyController(RequestController):
    SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE",
                         "PATCH", "PUT", "OPTIONS")

    def initialize(self, target: str,  not_allow: Dict = None):
        self.target = target
        self.not_allow = not_allow

    async def get(self, route): await self.__proxy(route)
    async def post(self, route): await self.__proxy(route)
    async def put(self, route): await self.__proxy(route)
    async def delete(self, route): await self.__proxy(route)
    async def patch(self, route): await self.__proxy(route)
    async def options(self, route): await self.__proxy(route)
    async def head(self, route): await self.__proxy(route)

    async def __proxy(self, route):
        if self.not_allow:
            rs = [x for x in self.not_allow if re.match(x, route)]
            for r in rs:
                if self.not_allow[r] and self.request.method.lower() in self.not_allow[r]:
                    self.set_status(405)
                    return
                elif not self.not_allow[r]:
                    self.set_status(405)
                    return

        url = '{}/{}?{}'.format(self.target, route, self.request.query)
        cookies = {k: v.output() for k, v in self.cookies.items()}
        response = await self.component_services.invoke_async(
            url, self.request.method.lower(), data=self.request.body, headers=self.request.headers, cookies=cookies)

        self.set_status(response.status_code)
        for key in response.headers:
            self.set_header(key, response.headers[key])
        for key in response.cookies:
            self.set_cookie(key, response.cookies[key])
        self.write(response.content)
