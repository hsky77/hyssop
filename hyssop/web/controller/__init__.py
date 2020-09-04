# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 27th 2020

This module contains the "yaml" configurable controller classes for hyssop application.

    - to create and setup controller api:

        0. the hierarchy of folders and files looks like:

            server_directory/
                server_config.yaml
                controller/
                    __init__.py
                    foo.py

        1. "__init__.py" defines the controllers:
            from hyssop.web.controller import ControllerType

            class ExControllerType(ControllerType):
                Foo = ('foo', 'foo', 'Foo')

        2. "foo.py" contains the controller class:

            from hyssop.web.controller.tornado import RequestController

            class Foo(RequestController):

                def initialize(self, p1, **kwds):
                    self.p1 = p1

                async def get(self):
                    self.write('Hello Workd: ', self.p1)

        3. setup component block of "server_config.yaml" to tell hyssop server load the extend components "Foo":

            controller:                 # block to setup controllers
                /foo:                   # api route
                    enum: foo           # tells to load foo controller class
                    params:
                        p1: xxxx        # parameter p1 of Foo.initialize()

Modified By: hsky77
Last Updated: September 1st 2020 14:53:09 pm
'''

from typing import List, Dict

from .. import LocalCode_Failed_To_Load_Controller
from ...util import join_path, BaseLocal
from .base import ControllerType
from ..config_validator import WebConfigControllerValidator


class DefaultControllerType(ControllerType):
    Frontend = ('frontend', 'tornado.web', 'StaticFileHandler')


class UnitTestControllerType(ControllerType):
    TestController = (
        'test_api', 'tornado.unittest_controller', 'TestController')
    TestStreamDownloadController = (
        'test_download', 'tornado.unittest_controller', 'TestStreamDownloadController')
    TestWebsocketController = (
        'test_socket', 'tornado.unittest_controller', 'TestWebsocketController')
    TestStreamUploadController = (
        'test_bytes_upload', 'tornado.unittest_controller', 'TestStreamUploadController')

def _get_controller_enum(key: str, contoller_types: List[ControllerType]):
    for contoller_type in contoller_types:
        try:
            return contoller_type(key)
        except:
            continue


def get_controllers(server_setting: Dict, server_dir: str = None) -> List:
    from tornado.web import StaticFileHandler
    from .. import Controller_Module_Folder
    controllers = []
    if Controller_Module_Folder in server_setting and isinstance(server_setting[Controller_Module_Folder], dict):
        contoller_types = [DefaultControllerType, UnitTestControllerType]
        try:
            extend_controller_type = ControllerType.get_controller_enum_class()
            contoller_types = extend_controller_type + \
                contoller_types if extend_controller_type else contoller_types
        except:
            pass

        # validate controller config
        WebConfigControllerValidator(server_setting[Controller_Module_Folder])

        for path, v in server_setting[Controller_Module_Folder].items():
            if 'enum' in v:
                t = _get_controller_enum(v['enum'], contoller_types)
                if t is None:
                    raise ImportError(BaseLocal.get_message(
                        LocalCode_Failed_To_Load_Controller, server_dir, v['enum']))
                cls_type = t.import_class()

                params = v['params'] if 'params' in v and v['params'] is not None else {}
                if issubclass(cls_type, StaticFileHandler):
                    server_setting['static_handler_class'] = cls_type
                    if 'path' in params:
                        params['path'] = join_path(server_dir, params['path'])

                controllers.append((path, cls_type, params))

    return controllers, server_setting
