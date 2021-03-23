# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: November 21st 2020

Modified By: hsky77
Last Updated: March 23rd 2021 00:28:43 am
'''

import os

from hyssop.util import join_path
from hyssop.command import CommandProcessor


class AioHttpCommandProcessor(CommandProcessor):
    Command_Start_Server = 'start'

    def __init__(self):
        super().__init__()

        start_parser = self.command_parsers.add_parser(
            AioHttpCommandProcessor.Command_Start_Server, help='start server with specfied server project directory path')
        start_parser.add_argument(self.args_key_project_directory,
                                  help='server project directory path')
        start_parser.add_argument('-s', '--http_server', action='store_true',
                                  help='start application on tornado http server')
        start_parser.set_defaults(
            command=AioHttpCommandProcessor.Command_Start_Server)

    def start(self) -> None:
        from .server import AioHttpServer
        server = AioHttpServer(self.project_dir)
        server.start()

    def _create_project_controller_files(self):
        if not os.path.isdir(self.project_controller_dir):
            os.makedirs(self.project_controller_dir)

        with open(join_path(self.project_controller_dir, '__init__.py'), 'w') as f:
            f.write('''\
from hyssop.project.web import ControllerType

class HelloControllerTypes(ControllerType):
    HelloController = ('hello_world', 'hello', 'hello')
    HelloViewController = ('hello_view', 'hello', 'HelloView')
''')

        with open(join_path(self.project_controller_dir, 'hello.py'), 'w') as f:
            f.write('''\
from aiohttp import web

from hyssop_aiohttp import routes, AioHttpView

class HelloView(AioHttpView):
    async def get(self):
        """
        ---
        tags:
        - hello view
        summary: hello world view get
        description: simple test controller
        produces:
        - text/html
        responses:
            200:
                description: return hello view message
        """
        return web.Response(text="Hello, world view")

@routes.get('/hello')
async def hello(request):
    """
    ---
    tags:
    - hello
    summary: hello world get
    description: simple test controller
    produces:
    - text/html
    responses:
        200:
            description: return hello message
    """
    return web.Response(text="Hello, world")
''')

    def _create_project_config_files(self):
        with open(self.project_config_file, 'w') as f:
            f.write('''\
name: hyssop Server
port: 8888
debug: False
doc:
  description: hello api
cors:
  - origin: '*'
    allow_credentials: True
    expose_headers: '*'
    allow_headers: '*'
component:
  hello: 
    p1: 'This is p1'
controller:
  /hello_view:
    enum: hello_view
aiohttp:
  route_decorators: 
    - 'hello_world'
''')

    def _create_project_requirement_files(self):
        # requirement
        import hyssop
        from . import __name__, Version
        with open(self.project_requirement_file, 'w') as f:
            f.write('{}>={}\n'.format(hyssop.__name__, hyssop.Version))
            f.write('{}>={}\n'.format(__name__, Version))
