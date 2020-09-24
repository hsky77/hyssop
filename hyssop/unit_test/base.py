# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: September 24th 2020 12:13:59 pm
'''

import time
from unittest import TestCase
from typing import List, Dict, Any

from ..util import DynamicTypeEnum, Worker

from ..web.server import HyssopServer
from ..web.constants import Component_Module_Folder, Controller_Module_Folder


class UnitTestTypes(DynamicTypeEnum):
    """base abstract unitest enum class"""

    @staticmethod
    def get_unittest_enum_class() -> List[DynamicTypeEnum]:
        from ..web import Unittest_Module_Folder
        try:
            return DynamicTypeEnum.get_dynamic_class_enum_class(Unittest_Module_Folder)
        except:
            pass

    def import_class(self):
        return super().import_class(cls_type=UnitTestCase)


class UnitTestCase(TestCase):
    """hyssop unittest case abstract class"""

    def test(self):
        raise NotImplementedError()


class UnitTestServer():
    default_component_setting = {
        'localization': {'dir': None},
        'logger': {'dir': 'files/logs', 'log_to_resources': False, 'log_to_console': False},
        'executor': {'worker_count': 3},
        'services':
        {
            'async_connection_limit': 20,
            'async_connection_limit_pre_host': 8,
            'routes': {}
        }
    }

    def __init__(self, name: str = 'UT Server', port: int = 58564, debug: bool = True):
        self._config = {
            'name': name,
            'port': port,
            'debug': debug,
            Component_Module_Folder: self.default_component_setting,
            Controller_Module_Folder: {}
        }

        self.server_exception = None
        self._server = HyssopServer()

    @property
    def running(self):
        return self._running if hasattr(self, '_running') else False

    def validate_config(self, component_config: Dict[str, Any] = None, controller_config: [str, Any] = None) -> None:
        if component_config:
            from ..web.config_validator import WebConfigComponentValidator
            WebConfigComponentValidator(component_config)

        if controller_config:
            from ..web.config_validator import WebConfigControllerValidator
            WebConfigControllerValidator(controller_config)

    def set_config(self, dir_path: str, component_config: Dict[str, Any] = None, controller_config: [str, Any] = None) -> None:
        from ..web.config_validator import WebConfigValidator

        self._root_dir = dir_path

        if component_config:
            self._config[Component_Module_Folder] = {
                **self._config[Component_Module_Folder], **component_config}

        if controller_config:
            self._config[Controller_Module_Folder] = {
                **self._config[Controller_Module_Folder], **controller_config}

        WebConfigValidator(self._config)

    def start(self):
        self._worker = Worker('server_worker')
        self._worker.run_method(self._start, self._server, self._root_dir, self._config,
                                on_exception=self._on_worker_exception)

        while not self.running:
            if self.server_exception:
                raise self.server_exception from self.server_exception
            time.sleep(0.5)

    def stop(self):
        if self._server:
            self._server.stop()
            self._server = None
            self._running = False

        if self._worker:
            self._worker.dispose()
            while self._worker.is_func_running:  # wait for server stoped
                time.sleep(0)

            self._worker = None

    def _start(self, server: HyssopServer, root_dir: str, config: dict):
        from tornado.ioloop import IOLoop
        IOLoop().make_current()

        server.init(root_dir, config=config)
        self._running = True
        server.start()

    def _on_worker_exception(self, e: Exception):
        self._running = False
        self.server_exception = e
