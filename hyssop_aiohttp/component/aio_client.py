# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
    AioClientComponent:

        - managing url route and service apis and provide inovke methons:

        component:
            aio_client:
                async_connection_limit:             <int>   # the connections limitation in async mode
                async_connection_limit_pre_host:    <int>   # the connections limitation of each host in async mode
                routes:
                    url:                            <str>
                        name:   api_route           <str>
                    url:                            <str>
                        etc...

File created: January 1st 2021

Modified By: hsky77
Last Updated: January 2nd 2021 09:16:54 am
'''

from typing import Callable

from aiohttp import web
from aiohttp import TCPConnector, ClientSession, ClientResponse

from hyssop.project.config_validator import ConfigContainerMeta, ConfigElementMeta, ConfigScalableElementMeta
from hyssop.project.component import Component, ComponentManager, ConfigComponentValidator

ConfigComponentValidator.set_cls_parameters(
    ConfigContainerMeta(
        'aio_client', False,
        ConfigElementMeta('async_connection_limit', int, False),
        ConfigElementMeta('async_connection_limit_pre_host', int, False),
        ConfigContainerMeta('routes', False,
                            ConfigScalableElementMeta(str, str)
                            )
    )
)


class AioClientComponent(Component):
    """default component for managing url route and service apis"""

    STREAMING_CHUNK_SIZE = 8192

    @property
    def async_client(self):
        if not hasattr(self, 'aclient'):
            self.aclient = ClientSession(connector=TCPConnector(
                limit=self.async_connection_limit, limit_per_host=self.async_connection_limit_pre_host))
        return self.aclient

    def init(self, component_manager: ComponentManager, **kwargs) -> None:
        self.async_connection_limit = kwargs.get('async_connection_limit', 30)
        self.async_connection_limit_pre_host = kwargs.get(
            'async_connection_limit_pre_host', 10)
        self.routes = kwargs.get('routes', {})

    async def invoke(self,
                     service_name_or_url: str,
                     method: str = 'get',
                     sub_route: str = '',
                     streaming_callback: Callable[[bytes], None] = None,
                     chunk_size: int = STREAMING_CHUNK_SIZE,
                     **kwargs) -> ClientResponse:
        """
        This function wraps aiohttp.ClientSession.request(). That means this function accepts the same parameters as aiohttp.ClientSession.request().
        The returned response is requests.Response to allow the similar usage of the response instance as self.invoke()

        Note: 
            use params= {} to send query parameters when method is 'get' or 'delete'
            use data= {} to send body parameters when method is the others
        """

        url = self.routes[service_name_or_url] if service_name_or_url in self.routes else service_name_or_url

        if not sub_route == '' and not sub_route == None:
            url = url if url[-1] == '/' else url + '/'
            url = '{}{}'.format(url, sub_route)

        if callable(streaming_callback):
            async with self.async_client.request(method, url, **kwargs) as response:
                async for chunk in response.content.iter_chunked(chunk_size):
                    streaming_callback(chunk)
        else:
            async with self.async_client.request(method, url, **kwargs) as response:
                await response.read()
                return response

    async def convert_web_response(self, response: ClientResponse) -> web.Response:
        res = web.Response(status=response.status, text=await response.text(), headers=response.headers)
        for name in response.cookies:
            res.set_cookie(name, response.cookies[name])
        return res

    async def dispose(self, component_manager: ComponentManager):
        if hasattr(self, 'aclient') and self.aclient:
            await self.aclient.close()
