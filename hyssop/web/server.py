# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: October 1st 2020 21:45:14 pm
'''


import os
from typing import Awaitable, Dict


from tornado.web import url

from ..util import join_path, DynamicTypeEnum, join_to_abs_path, BaseLocal
from .component import (ComponentManager, ComponentTypes, DefaultComponentTypes,
                        create_server_component_manager)

from . import LocalCode_File_Not_Found, Hyssop_Web_Config_File


class HyssopServer():
    def start(self):
        from tornado.ioloop import IOLoop, PeriodicCallback
        PeriodicCallback(self.app.do_exit, 1000).start()
        IOLoop.current().start()

    def stop(self):
        if self.app:
            self.app.exit()

    def start_periodic_callback(self, awaitable_func: Awaitable, *args, interval: int = 1000, **kwargs) -> None:
        from tornado.ioloop import PeriodicCallback
        from inspect import iscoroutinefunction
        if iscoroutinefunction(awaitable_func):
            PeriodicCallback(lambda: self.__periodic_callback_decorator(
                awaitable_func, *args, **kwargs), interval).start()

    async def __periodic_callback_decorator(self, func, *args, **kwargs):
        if not self.app.exiting:
            await func(*args, **kwargs)

    def init(self, server_dir: str, use_http_server: bool = False, config: Dict = None, **kwargs) -> None:
        self.root_dir = join_to_abs_path(server_dir)
        self.config_path = join_to_abs_path(
            server_dir, Hyssop_Web_Config_File)

        if config:
            self.config = config
            self.config_path = None
        else:
            with open(self.config_path, 'r') as f:
                import yaml
                from .config_validator import WebConfigRootValidator
                validator = WebConfigRootValidator(
                    yaml.load(f, Loader=yaml.SafeLoader))
                self.config = validator.parameter

        self._make_app()

        if use_http_server or 'ssl' in self.config:
            from tornado.web import HTTPServer

            if 'ssl' in self.config:
                if not os.path.isfile(join_path(self.config['ssl']['crt'])):
                    raise FileNotFoundError(BaseLocal.get_message(
                        LocalCode_File_Not_Found, join_path(self.config['ssl']['crt'])))
                if not os.path.isfile(join_path(self.config['ssl']['key'])):
                    raise FileNotFoundError(BaseLocal.get_message(
                        LocalCode_File_Not_Found, join_path(self.config['ssl']['key'])))

                import ssl
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(join_path(self.config['ssl']['crt']),
                                        join_path(self.config['ssl']['key']))
                if 'ca' in self.config['ssl']:
                    if not os.path.isfile(join_path(self.config['ssl']['ca'])):
                        raise FileNotFoundError(BaseLocal.get_message(
                            LocalCode_File_Not_Found, join_path(self.config['ssl']['ca'])))
                    ssl_ctx.load_verify_locations(
                        join_path(self.config['ssl']['ca']))

                self.server = HTTPServer(self.app, ssl_options=ssl_ctx)
            else:
                self.server = HTTPServer(self.app)

            self.server.listen(self.config['port'])
        else:
            self.app.listen(self.config['port'])

    def _make_app(self):
        from .controller import get_controllers

        settings = {
            'root_dir': self.root_dir,
            'config_path': self.config_path,
            **self.config
        }

        controllers, settings = get_controllers(settings, self.root_dir)

        self.app = self._make_app_instance(controllers, settings)
        self.app.init_application_mixin(settings)

    def _setup_api_doc(self, controllers, settings):
        """
        setup swagger api doc urls, parameter "settings" is a dict that has "doc" like:

        {
            'doc': {
                'swagger_url': '/api/doc',
                'api_base_url': '/',
                'description': 'Swagger API definition',
                'api_version': '1.0.0',
                'title': 'Swagger API'
            }
        }
        """
        if 'doc' in settings:
            api_route = '/api/doc'
            description = 'Swagger API definition'
            api_version: str = '1.0.0'
            title = 'Swagger API'
            contact = ''

            if type(settings['doc']) is dict:
                api_route = settings['doc'].get('api_route', api_route)
                description = settings['doc'].get('description', description)
                api_version = settings['doc'].get('version', api_version)
                title = settings['doc'].get('title', title)
                contact = settings['doc'].get('contact', contact)

            from tornado_swagger.setup import setup_swagger
            controllers = [url(route, c, kwargs, name=c.__name__)
                           for route, c, kwargs in controllers]
            setup_swagger(controllers, description=description,
                          api_version=api_version, title=title, contact=contact, swagger_url=api_route)

        return controllers

    def _make_app_instance(self, controllers, settings):
        if "framework" in settings:
            if settings["framework"] == "tornado":
                from .application.tornado import TornadoApplication
                from tornado_swagger.setup import setup_swagger
                controllers = self._setup_api_doc(controllers, settings)
                return TornadoApplication(controllers, **settings)
        else:
            from .application.tornado import TornadoApplication
            from tornado_swagger.setup import setup_swagger
            controllers = self._setup_api_doc(controllers, settings)
            return TornadoApplication(controllers, **settings)
