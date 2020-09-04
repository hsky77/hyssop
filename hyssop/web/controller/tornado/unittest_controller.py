# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 20th 2020

Modified By: hsky77
Last Updated: September 3rd 2020 11:18:07 am
'''


from . import RequestController, WebSocketController, StreamingDownloadController, StreamingUploadController
from ...constants import GB


class TestController(RequestController):
    def test_method(self, value: int):
        return value

    async def get(self):
        """
        ---
        tags:
        - test api
        summary: run for test base controller get
        description: base api test
        produces:
        - text/html
        responses:
            200:
              description: return test text
        """
        response = await self.component_services.invoke_async('test_www', 'get', params={'text': 'hello this is test'})
        self.write(response.text + '\n')

        response = await self.component_services.invoke_async('test_api', 'post', data={'value': 'hello this is test'})
        self.log_info(response.text)
        self.write(response.text + '\n')

        response = await self.component_services.invoke_async('test_api', 'put', data={'value': 'hello this is test'})
        self.log_info(response.text)
        self.write(response.text + '\n')

        response = await self.component_services.invoke_async('test_api', 'delete', params={'id': 'hello this is test'})
        self.log_info(response.text)
        self.write(response.text + '\n')

        with self.component_executor.get_executor() as executor:
            result = executor.run_method(self.test_method, 1)

        with self.component_executor.get_executor() as executor:
            result = await executor.run_method_async(self.test_method, 1)

    async def post(self):
        """
        ---
        tags:
        - test api
        summary: run for test base controller post
        description: base api test
        produces:
        - text/html
        responses:
            200:
              description: return test text
        """

        self.write('I got this post value: {}'.format(
            self.get_body_argument('value')))

    async def put(self):
        """
        ---
        tags:
        - test api
        summary: run for test base controller put
        description: base api test
        produces:
        - text/html
        responses:
            200:
              description: return test text
        """

        self.write('I got this put value: {}'.format(
            self.get_body_argument('value')))

    async def delete(self):
        """
        ---
        tags:
        - test api
        summary: run for test base controller delete
        description: base api test
        produces:
        - text/html
        responses:
            200:
              description: return test text
        """

        self.write('I got this id to delete: {}'.format(
            self.get_query_argument('id')))


class TestStreamDownloadController(StreamingDownloadController):
    async def _prepare_binary(self):
        self.set_header('Content-Disposition',
                        'attachment; filename=' + 'test.data')
        b = b''.ljust(1*GB, b'0')
        return b


class TestStreamUploadController(StreamingUploadController):
    async def prepare(self):
        self.buffer = []

    def _on_chunk_received(self, headers, chunk, bytes_size_received):
        self.buffer.append(chunk)

    def _on_data_received(self, headers, bytes_size_received):
        data = b''.join(self.buffer)
        if 'charset' in self.content_mime_options:
            data = data.decode(self.content_mime_options['charset'])
        self.write(data)


class TestWebsocketController(WebSocketController):
    live_web_sockets = set()

    def on_message(self, message):
        self.send_message(message)

    def open(self):
        self.set_nodelay(True)
        self.live_web_sockets.add(self)

    def on_close(self):
        self.live_web_sockets.remove(self)

    def send_message(self, message):
        removable = set()
        for ws in self.live_web_sockets:
            if not ws.ws_connection or not ws.ws_connection.stream.socket:
                removable.add(ws)
            else:
                ws.write_message(message)
        for ws in removable:
            self.live_web_sockets.remove(ws)
