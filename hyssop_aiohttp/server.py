# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: November 21st 2020

Modified By: hsky77
Last Updated: December 27th 2020 07:51:33 am
'''

import os
import inspect
from typing import List, Any
from multidict import MultiDictProxy

from aiohttp import web

from hyssop.project.web import WebApplicationMinin
from hyssop.project.component import add_module_default_logger

add_module_default_logger(['aiohttp.access', 'aiohttp.web'])

routes = web.RouteTableDef()


class AioHttpApplication(web.Application, WebApplicationMinin):
    @property
    def port(self) -> int:
        return self.project_config['port']

    def load_project(self, project_dir: str) -> None:
        super().load_project(project_dir)

        self._debug = self.project_config.get('debug', False)

        for controller in self.project_controllers:
            if inspect.isclass(controller[1]) and issubclass(controller[1], web.View):
                self.router.add_view(controller[0], controller[1])

        if 'aiohttp' in self.project_config and type(self.project_config['aiohttp']) is dict:
            if 'static_file' in self.project_config['aiohttp']:
                for k, v in self.project_config['aiohttp']['static_file'].items():
                    path = self.project_dir + k
                    if not os.path.isdir(path):
                        os.mkdir(path)
                    self.add_routes([web.static(k, path, **v)])

        self.add_routes(routes)

        if 'doc' in self.project_config and type(self.project_config['doc']) is dict:
            from aiohttp_swagger import setup_swagger

            api_route = self.project_config['doc'].get('api_route', '/api/doc')
            description = self.project_config['doc'].get(
                'description', 'Swagger API definition')
            api_version = self.project_config['doc'].get('version', '1.0.0')
            title = self.project_config['doc'].get('title', 'Swagger API')
            contact = self.project_config['doc'].get('contact', '')

            setup_swagger(self, swagger_url=api_route, description=description,
                          api_version=api_version, title=title, contact=contact)

    async def after_project_loaded(self, app: web.Application):
        from hyssop.project.component import DefaultComponentTypes
        self.component_manager.invoke(
            DefaultComponentTypes.Logger, 'update_default_logger', self.project_config['debug'])

    async def dispose(self, app: web.Application):
        await self.component_manager.dispose_components()


class AioHttpServer():
    def __init__(self, project_dir: str):
        self.app = AioHttpApplication()
        self.app.load_project(project_dir)
        self.app.on_startup.append(self.app.after_project_loaded)
        self.app.on_cleanup.append(self.app.dispose)

    def start(self):
        web.run_app(self.app, port=self.app.port,
                    ssl_context=self.app.project_ssl_context)


class AioHttpRequest(web.Request):
    @property
    def app(self) -> AioHttpApplication:
        return super().app


class AioHttpView(web.View):
    @property
    def request(self) -> AioHttpRequest:
        return super().request

    async def get_argument(self, name: str, default: Any = None) -> Any:
        if self.request.method in ['GET', 'DELETE']:
            return self.request.query.get(name, default)
        elif self.request.method in ['POST', 'PUT']:
            if not hasattr(self, '_parsed_body'):
                if self.request.content_type == 'application/json':
                    self._parsed_body = await self.request.json()
                else:
                    self._parsed_body = await self.request.post()
            return self._parsed_body.get(name, default)
        else:
            raise web.HTTPBadRequest()

    async def get_arguments_dict(self, args: List[str] = None) -> MultiDictProxy:
        if not hasattr(self, '_parsed_body'):
            if self.request.content_type == 'application/json':
                self._parsed_body = await self.request.json()
            else:
                self._parsed_body = await self.request.post()

        data = {**self.request.query, **self._parsed_body}
        if args:
            return {k: v for k, v in data.items() if k in args}
        else:
            return data