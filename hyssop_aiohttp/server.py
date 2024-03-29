# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: November 21st 2020

Modified By: hsky77
Last Updated: May 7th 2022 10:01:06 am
'''

import os
import inspect
import asyncio
from typing import List, Any
from multidict import MultiDictProxy

from aiohttp import web
import aiohttp_cors

from hyssop.project.web import WebApplicationMinin, ControllerType
from hyssop.project.component import add_module_default_logger, add_default_component_types

from hyssop_aiohttp.component import AioHttpComponentTypes

add_default_component_types(AioHttpComponentTypes)

add_module_default_logger(['aiohttp.access', 'aiohttp.web', 'aiohttp.server'])

routes = web.RouteTableDef()


class AioHttpRequest(web.Request):
    @property
    def app(self) -> "AioHttpApplication":
        return super().app

    async def get_argument(self, name: str, *default) -> Any:
        """
        Get argument from query string or body data. Return default or raise HTTPBadRequest exception if that does not exist.
        """
        if not hasattr(self, '_parsed_body'):
            if self.content_type == 'application/json':
                self._parsed_body = await self.json()
            else:
                self._parsed_body = await self.post()

        data = {**self.query, **self._parsed_body}
        if name in data:
            return data[name]
        else:
            if len(default) > 0:
                return default[0]
            else:
                raise web.HTTPBadRequest(text=str(KeyError(name)))

    async def get_arguments_dict(self, args: List[str] = None) -> MultiDictProxy:
        """
        Get arguments dict from query string or body data with indicated args.
        """
        if not hasattr(self, '_parsed_body'):
            if self.content_type == 'application/json':
                self._parsed_body = await self.json()
            else:
                self._parsed_body = await self.post()

        data = {**self.query, **self._parsed_body}
        if args:
            return {k: v for k, v in data.items() if k in args}
        else:
            return data


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
            if 'www' in self.project_config['aiohttp']:
                path = self.project_dir + '/' + \
                    self.project_config['aiohttp']['www']
                if not os.path.isdir(path):
                    os.mkdir(path)
                self.add_routes(
                    [web.static('/', path)])
            if 'route_decorators' in self.project_config['aiohttp']:
                controller_types = ControllerType.get_controller_enum_class()
                for key in self.project_config['aiohttp']['route_decorators']:
                    if len(controller_types) < 1:
                        raise KeyError(key)

                    type_cls = None
                    for controller_type in controller_types:
                        try:
                            type_cls = controller_type(key)
                            break
                        except:
                            continue

                    if type_cls:
                        try:
                            _ = type_cls.import_class()
                        except:
                            _ = type_cls.import_function()
                    else:
                        raise KeyError(key)

        self.add_routes(routes)

        # Setup aiohttp swagger
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

        # Setup Cors settings
        if 'cors' in self.project_config:
            cors_settings = {}
            for cors_setting in self.project_config['cors']:
                cors_settings[cors_setting['origin']] = aiohttp_cors.ResourceOptions(**{
                    k: v for k, v in cors_setting.items() if not k == 'origin'
                })
            cors = aiohttp_cors.setup(
                self, defaults=cors_settings)

            for route in list(self.router.routes()):
                cors.add(route)

    async def after_project_loaded(self, app: web.Application):
        from hyssop.project.component import DefaultComponentTypes
        self.component_manager.invoke(
            DefaultComponentTypes.Logger, 'update_default_logger', self.project_config['debug'])

        await self.component_manager.boardcast_async('on_before_server_start')

    async def dispose(self, app: web.Application):
        await self.component_manager.dispose_components()

    def _make_request(
        self,
        message,
        payload,
        protocol,
        writer,
        task: "asyncio.Task[None]",
        _cls: web.Request = web.Request,
    ) -> web.Request:
        return super()._make_request(
            message, payload, protocol, writer, task, AioHttpRequest)


class AioHttpServer():
    def __init__(self, project_dir: str):
        self.app = AioHttpApplication()
        self.app.load_project(project_dir)
        self.app.on_startup.append(self.app.after_project_loaded)
        self.app.on_cleanup.append(self.app.dispose)

    def start(self):
        web.run_app(self.app, port=self.app.port,
                    ssl_context=self.app.project_ssl_context)


class AioHttpView(web.View, aiohttp_cors.mixin.CorsViewMixin):
    @property
    def request(self) -> AioHttpRequest:
        return super().request

    async def get_argument(self, name: str, default: Any = None) -> Any:
        return await self.request.get_argument(name, default)

    async def get_arguments_dict(self, args: List[str] = None) -> MultiDictProxy:
        return await self.request.get_arguments_dict(args)
