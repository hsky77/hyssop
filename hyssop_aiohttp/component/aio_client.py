# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
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
Last Updated: April 6th 2025 07:38:48 am
"""

from inspect import iscoroutinefunction
from typing import Callable, Optional, Dict, Any
from hyssop.component import Component
from aiohttp import ClientResponse, ClientSession, TCPConnector, web
from pydantic import BaseModel, Field


class AioClientComponentConfig(BaseModel):

    async_connection_limit: int = Field(default=30, description="async http connection limi.")
    async_connection_limit_pre_host: int = Field(default=10, description="async http connection limi of each host.")
    routes: Dict[str, Any] = Field(default_factory=dict, description="service url routes")


class AioClientComponent(Component[AioClientComponentConfig]):
    """default component for managing url route and service apis"""

    STREAMING_CHUNK_SIZE = 8192

    @property
    def async_client(self):
        if self.aclient is None:
            self.aclient = ClientSession(
                connector=TCPConnector(
                    limit=self.config.async_connection_limit, limit_per_host=self.config.async_connection_limit_pre_host
                )
            )
        return self.aclient

    def init(self) -> None:
        self.aclient: Optional[ClientSession] = None

    async def invoke(
        self,
        service_name_or_url: str,
        method: str = "get",
        sub_route: str = "",
        streaming_callback: Optional[Callable[[bytes], None]] = None,
        chunk_size: int = STREAMING_CHUNK_SIZE,
        **kwargs
    ) -> ClientResponse:
        """
        This function wraps aiohttp.ClientSession.request().
        That means this function accepts the same parameters as aiohttp.ClientSession.request().
        The returned response is requests.Response to allow the similar usage of the response instance as self.invoke()

        Note:
            use params= {} to send query parameters when method is 'get' or 'delete'
            use data= {} to send body parameters when method is the others
        """

        url = (
            self.config.routes[service_name_or_url]
            if self.config.routes and service_name_or_url in self.config.routes
            else service_name_or_url
        )

        if not sub_route == "" and sub_route is not None:
            url = url if url[-1] == "/" else url + "/"
            url = "{}{}".format(url, sub_route)

        if callable(streaming_callback):
            async with self.async_client.request(method, url, **kwargs) as response:
                async for chunk in response.content.iter_chunked(chunk_size):
                    if not iscoroutinefunction(streaming_callback):
                        streaming_callback(chunk)
                    else:
                        await streaming_callback(chunk)
                return response
        else:
            async with self.async_client.request(method, url, **kwargs) as response:
                await response.read()
                return response

    async def convert_web_response(self, response: ClientResponse) -> web.Response:
        res = web.Response(status=response.status, text=await response.text(), headers=response.headers)
        for name, value in response.cookies.items():
            res.set_cookie(name, value)  # type: ignore
        return res

    async def dispose(self):
        if self.aclient is not None:
            await self.aclient.close()
