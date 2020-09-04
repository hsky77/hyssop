# Copyright (C) 2019-Present the hyssop authors and contributors
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
server loads all default components in hyssop.web.component.DefaultComponentTypes when starting

    LocalizationComponent:

        - managing localized message via config setting such as:

        component:
            localization:
                dir: 'local'    # optional: Load the .csv files in the directory under project directory.
                lang: 'en'      # optional: Setup language, default: en.

    LoggerComponent:

        - managing logger via config setting such as:

        component:
            logger:
                log_to_resources: False     # optional: Enable log to resources
                log_to_console: False       # optional: Enable log to console
                dir: 'logs'                 # optional. Log to files in the folder under porject directory if specified

    CallbackComponent:

        - managing callback function by enum types, no configuration settings needed

    ExecutorComponent:

        - managing executor to execute the given functions and arguments

        component:
            executor:
                worker_count: 1      # The maximum of workers is 2

    ServicesComponent:

        - managing url route and service apis and provide inovke methons:

        component:
            services:
                async_connection_limit:             <int>   # the connections limitation in async mode
                async_connection_limit_pre_host:    <int>   # the connections limitation of each host in async mode
                routes:
                    url:                            <str>
                        name:   api_route           <str>
                    url:                            <str>
                        etc...

Last Updated: September 4th 2020 14:27:50 pm
'''

import logging
import requests

from datetime import datetime
from enum import Enum
from typing import Callable, Any, List, Dict, ByteString

from aiohttp import ClientResponse, TCPConnector, ClientSession

from . import Component, ComponentManager, ComponentTypes
from ...util import ExecutorFactory, Executor, Callbacks, configure_colored_logging, join_path, BaseSyncLogger
from .mixin import FileLoggerMixin


class LocalizationComponent(Component):
    """default component for managing localized message by config setting"""

    def init(self, component_manager: ComponentManager, lang: str = 'en', **kwargs) -> None:
        import os
        from hyssop.util import BaseLocal
        self.local = BaseLocal

        self.dir = kwargs.get('dir', None)
        if self.dir is not None:
            self.dir = join_path(kwargs.get('root_dir', ''), self.dir)
            self.local.import_csvs_from_directory(self.dir)

        if lang is not None:
            self.local.set_language(lang)

    def info(self) -> str:
        return {**super().info(), **{'info': self.local.get_info()}}

    @property
    def current_language(self) -> str:
        return self.local.current_language

    def set_language(self, lang: str) -> None:
        self.local.set_language(lang)

    def get_message(self, code: str, *args) -> str:
        """convert to localized message with code and following parameters"""
        return self.local.get_message(code, *args)


class LoggerComponent(FileLoggerMixin, Component):
    """default component for managing logger by server config"""

    default_loggers = []

    def __init__(self, component_type: ComponentTypes):
        super().__init__(component_type)
        configure_colored_logging()
        self.loggers = {}
        self.kwargs = None

    def init(self, component_manager: ComponentManager, **kwargs) -> None:
        self.kwargs = kwargs
        self.log_level = logging.INFO
        self.log_echo = self.kwargs.get('log_to_console', False)
        self.log_to_resources = self.kwargs.get('log_to_resources', False)

    def get_logger(self, name: str, *args, sub_dir: str = '', mode: str = 'a', encoding: str = 'utf-8', echo: bool = False) -> BaseSyncLogger:
        """create and return logger object, sub_dir appends the path to configured log path"""
        logger = self.loggers[name] if name in self.loggers else None

        if not logger:
            logger = logging.getLogger(name)

            if self.log_to_resources:
                self.update_file_handler(
                    logger, sub_dir, mode, encoding, **self.kwargs)
            else:
                self.remove_file_handler(logger, sub_dir, **self.kwargs)

            self.loggers[name] = logger

        if logger:
            logger.setLevel(self.log_level)
            logger.propagate = self.log_echo or echo

        return logger

    def update_default_logger(self, debug: bool = False) -> None:
        self.log_level = logging.DEBUG if debug else self.log_level

        for name in self.default_loggers:
            self.get_logger(name)

        self.loggers.clear()


class CallbackComponent(Component):
    """default component for managing callback function by enum types"""

    def init(self, component_manager: ComponentManager, *arugs, **kwargs) -> None:
        self._callback_manager = {}

    def get_callback_obj(self, enum_cls: Enum) -> Callbacks:
        if not enum_cls in self._callback_manager:
            self._callback_manager[enum_cls] = Callbacks(enum_cls)
        return self._callback_manager[enum_cls]

    def add_callback(self, callback_enum_type: Enum, callback: Callable) -> None:
        if isinstance(callback_enum_type, Enum):
            enum_cls = type(callback_enum_type)
            if not enum_cls in self._callback_manager:
                self._callback_manager[enum_cls] = Callbacks(enum_cls)

            self._callback_manager[enum_cls].add_callback(
                callback_enum_type, callback)

    def remove_callback(self, callback_enum_type: Enum, callback: Callable) -> None:
        if isinstance(callback_enum_type, Enum):
            enum_cls = type(callback_enum_type)
            if enum_cls in self._callback_manager:
                self._callback_manager[enum_cls].remove_callback(
                    callback_enum_type, callback)

    def execute_callback(self, callback_enum_type: Enum, *args, **kwargs) -> None:
        from tornado.ioloop import IOLoop
        if isinstance(callback_enum_type, Enum):
            enum_cls = type(callback_enum_type)
            if enum_cls in self._callback_manager:
                self._callback_manager[enum_cls].execute_callback(
                    callback_enum_type, *args, **kwargs)

    async def execute_callback_async(self, callback_enum_type: Enum, *args, **kwargs) -> None:
        if isinstance(callback_enum_type, Enum):
            enum_cls = type(callback_enum_type)
            if enum_cls in self._callback_manager:
                await self._callback_manager[enum_cls].execute_callback_async(
                    callback_enum_type, *args, **kwargs)


class ExecutorComponent(Component):
    def init(self, component_manager: ComponentManager, worker_count: int = 1, **kwargs) -> None:
        self.executor_factory = ExecutorFactory(worker_limit=worker_count)
        self.disposing = False

    def info(self) -> Dict:
        return {**super().info(), **{
            'info': {
                'workers': self.executor_factory.worker_count
            }
        }}

    def run_method_in_queue(self,
                            func: Callable,
                            *args,
                            on_finish: Callable[[Any], None] = None,
                            on_exception: Callable[[Exception], None] = None,
                            **kwargs) -> None:
        if not self.disposing:
            self.executor_factory.run_method_in_queue(
                func, *args, on_finish=on_finish, on_exception=on_exception, **kwargs)

    def run_method(self, func: Callable, *args, **kwargs) -> Any:
        if not self.disposing:
            return self.executor_factory.run_method(func, *args, **kwargs)

    async def run_method_async(self, func: Callable, *args, **kwargs) -> Any:
        if not self.disposing:
            return await self.executor_factory.run_method_async(func, *args, **kwargs)

    def get_executor(self) -> Executor:
        return self.executor_factory.get_executor()

    def dispose(self, component_manager: ComponentManager) -> None:
        self.disposing = True
        self.executor_factory.dispose()


class ServicesComponent(Component):
    """default component for managing url route and service apis"""

    STREAMING_CHUNK_SIZE = 8192

    @property
    def async_client(self) -> ClientSession:
        if not hasattr(self, 'aclient'):
            self.aclient = ClientSession(connector=TCPConnector(
                limit=self.async_connection_limit, limit_per_host=self.async_connection_limit_pre_host))
        return self.aclient

    def init(self, component_manager: ComponentManager, **kwargs) -> None:
        self.async_connection_limit = kwargs.get('async_connection_limit', 30)
        self.async_connection_limit_pre_host = kwargs.get(
            'async_connection_limit_pre_host', 10)

        self.routes = {}
        routes = kwargs.get('routes', {})
        for url, apis in routes.items():
            for name, api in apis.items():
                self.routes[name] = '{}{}'.format(url, api)

    def invoke(self,
               service_name_or_url: str,
               method: str = 'get',
               sub_route: str = '',
               streaming_callback: Callable = None,
               chunk_size: int = STREAMING_CHUNK_SIZE,
               **kwargs) -> requests.Response:
        """
        This function wraps requests.request(). That means this function accepts the same parameters as requests.request()

        Note: 
            use params= {} to send query parameters when method is 'get' or 'delete'
            use data= {} to send body parameters when method is the others
        """
        url = self.routes[service_name_or_url] if service_name_or_url in self.routes else service_name_or_url

        if not sub_route == '' and not sub_route == None:
            url = '{}/{}'.format(url, sub_route)

        if callable(streaming_callback):
            with requests.request(method, url, stream=True, **kwargs) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=chunk_size):
                    streaming_callback(chunk)
                return response
        else:
            return requests.request(method, url, **kwargs)

    async def invoke_async(self,
                           service_name_or_url: str,
                           method: str = 'get',
                           sub_route: str = '',
                           streaming_callback: Callable[[bytes], None] = None,
                           chunk_size: int = STREAMING_CHUNK_SIZE,
                           **kwargs) -> requests.Response:
        """
        This function wraps aiohttp.ClientSession.request(). That means this function accepts the same parameters as aiohttp.ClientSession.request().
        The returned response is requests.Response to allow the similar usage of the response instance as self.invoke()

        Note: 
            use params= {} to send query parameters when method is 'get' or 'delete'
            use data= {} to send body parameters when method is the others
        """

        url = self.routes[service_name_or_url] if service_name_or_url in self.routes else service_name_or_url

        if not sub_route == '' and not sub_route == None:
            url = '{}/{}'.format(url, sub_route)

        result = requests.Response()
        dt = datetime.now()
        if callable(streaming_callback):
            async with self.async_client.request(method, url, **kwargs) as response:
                async for chunk in response.content.iter_chunked(chunk_size):
                    streaming_callback(chunk)
        else:
            async with self.async_client.request(method, url, **kwargs) as response:
                result._content = await response.read()

        result.status_code = response.status
        result.url = str(response.real_url)
        result.headers = {k: v for k, v in response.headers.items()}
        result.cookies = response.cookies
        result.history = response.history
        result.elapsed = datetime.now() - dt
        result.encoding = response.get_encoding()
        result.request = response.request_info
        return result

    async def dispose(self, component_manager: ComponentManager):
        if hasattr(self, 'aclient') and self.aclient:
            await self.aclient.close()
