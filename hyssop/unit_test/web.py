# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 20th 2020

Modified By: hsky77
Last Updated: August 27th 2020 16:19:09 pm
'''


import time
import asyncio

from ..web import Component_Module_Folder, Controller_Module_Folder
from .base import UnitTestCase, UnitTestServer
from ..util import join_path


class WebTestCase(UnitTestCase):
    def test(self):
        self.test_components()
        self.test_server()

    def test_server(self):
        from .. import Module_Path
        from ..web.component import DefaultComponentTypes, create_server_component_manager
        from ..web.component.default import ServicesComponent

        # start a test server
        dir_path = join_path(Module_Path, 'web')
        server = UnitTestServer()

        component_setting = {
            'services':
            {
                'routes': {
                    'https://www.google.com': {
                        'test_www': '/'
                    },
                    'http://localhost:58564': {
                        'test_api': '/test_api'
                    }
                }
            }
        }
        server.set_config(dir_path,
                          component_config=component_setting,
                          controller_config={
                              '/test_api': {
                                  'enum': 'test_api'},
                              '/test_download': {
                                  'enum': 'test_download'
                              },
                              '/test_socket': {
                                  'enum': 'test_socket'
                              },
                              '/test_bytes_upload': {
                                  'enum': 'test_bytes_upload'
                              }
                          })

        server.start()

        component_manager = create_server_component_manager(
            component_setting, dir_path)

        service: ServicesComponent = component_manager.get_component(
            DefaultComponentTypes.Service)

        try:
            # test request
            response = None
            while not response:
                if server.server_exception:
                    raise server.server_exception
                try:
                    # pass
                    response = service.invoke(
                        'http://localhost:58564/test_api')
                except:
                    time.sleep(0.5)

            self.assertEqual(response.status_code, 200)

            # test bytes upload
            from ..web.application.tornado import StreamUploadClient
            client = StreamUploadClient()
            response = client.send_bytes(
                'http://localhost:58564/test_bytes_upload', b'i am bytes')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, 'i am bytes')

            # # test web socket
            from ..web.application.tornado import WebSocketClient
            with WebSocketClient() as client:
                self.received_msg = None

                def received_ws_msg(msg):
                    self.received_msg = msg

                client.connect('ws://localhost:58564/test_socket',
                               on_message_callback=received_ws_msg)
                client.write_message('Hello There')

                while self.received_msg is None:  # wait for message come back
                    time.sleep(0)

                self.assertEqual(self.received_msg, 'Hello There')

        finally:
            server.stop()

    def test_components(self):
        import os
        from ..web.component import create_server_component_manager, DefaultComponentTypes
        from ..web.component.default import LocalizationComponent, LoggerComponent, CallbackComponent, ExecutorComponent, ServicesComponent
        from ..web.constants import LocalCode_Application_Closing
        from .. import Module_Path
        from ..util import join_path
        dir_path = join_path(Module_Path, 'web')

        component_setting = {
            'services':
            {
                'routes': {
                    'https://www.google.com': {
                        'test_www': '/'
                    }
                }
            }
        }

        component_manager = create_server_component_manager(
            component_setting, dir_path)

        self.test_func_runned = False

        try:
            # test default components:
            # localization
            local: LocalizationComponent = component_manager.get_component(
                DefaultComponentTypes.Localization)
            local.set_language('en')
            self.assertEqual(local.get_message(
                LocalCode_Application_Closing), 'stopping application')

            # log
            log: LoggerComponent = component_manager.get_component(
                DefaultComponentTypes.Logger)
            logger = log.get_logger('test_logger')
            logger.info('Test Message')
            for path in log.default_loggers + ['test_logger']:
                path = join_path(dir_path, 'files', 'logs', path + '.log')
                self.assertFalse(os.path.isfile(path))

            # callback
            from .util import UtilTestCase, TestCallbackType
            callbacks: CallbackComponent = component_manager.get_component(
                DefaultComponentTypes.Callback)
            UtilTestCase.test_callback(
                self, callbacks.get_callback_obj(TestCallbackType))

            # executor
            executor: ExecutorComponent = component_manager.get_component(
                DefaultComponentTypes.Executor)
            executor.run_method(UtilTestCase.test_func, self, 1, kwindex=2)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(executor.run_method_async(
                UtilTestCase.test_func, self, 1, kwindex=2))

            def test_func(result):
                self.test_func_runned = True

            executor.run_method_in_queue(UtilTestCase.test_func, self, 1,
                                         kwindex=2, on_finish=test_func)

            # services
            services: ServicesComponent = component_manager.get_component(
                DefaultComponentTypes.Service)
            response = services.invoke('test_www')
            self.assertEqual(response.status_code, 200)

        finally:
            # queue will run at this moment if this test runs too fast
            loop.run_until_complete(
                component_manager.boardcast_async('dispose', component_manager))
            self.assertTrue(self.test_func_runned)
