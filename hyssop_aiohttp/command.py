# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: November 21st 2020

Modified By: hsky77
Last Updated: April 6th 2025 07:47:14 am
"""

import os

from hyssop.utils.func import join_path
from hyssop.command import CommandProcessor

from .server import AioHttpHyssopProject
from . import Version


class AioHttpCommandProcessor(CommandProcessor):
    Command_Start_Server = "start"

    def __init__(self):
        super().__init__()

        start_parser = self.command_parsers.add_parser(
            AioHttpCommandProcessor.Command_Start_Server,
            help="start server with specfied server project directory path",
        )
        start_parser.add_argument(self.args_key_project_directory, help="path of server project directory")
        start_parser.set_defaults(command=AioHttpCommandProcessor.Command_Start_Server)

    def create_project(self):
        self.project = AioHttpHyssopProject(self.project_dir)

    def start(self) -> None:
        from .server import AioHttpServer

        server = AioHttpServer(self.project_dir)
        server.start()

    def version(self):
        print("hyssop-aiohttp {}".format(Version))

    def _create_project_controller_files(self):
        if not os.path.isdir(self.project.controller_dir):
            os.makedirs(self.project.controller_dir)

        with open(join_path(self.project.controller_dir, "__init__.py"), "w") as f:
            f.write(
                """\
from hyssop_aiohttp.server import ControllerTypes
from .hello import hello


class HelloControllerTypes(ControllerTypes):
    hello_world = hello
"""
            )

        with open(join_path(self.project.controller_dir, "hello.py"), "w") as f:
            f.write(
                """\
from aiohttp import web

from hyssop_aiohttp.server import routes, AioHttpRequest
"""
                f"from {self.project.project_dir_name}.component import HelloComponentTypes"
                '''


@routes.get("/hello")
async def hello(request: web.Request):
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
    if not isinstance(request, AioHttpRequest):
        raise TypeError("request must be AioHttpRequest")
    comp = request.app.component_manager.get_component(HelloComponentTypes.Hello)
    return web.Response(text=comp.hello())
'''
            )

    def _create_project_config_files(self):
        with open(self.project.config_file, "w") as f:
            f.write(
                """\
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
"""
            )

    def _create_project_requirement_files(self):
        # requirement
        import hyssop
        from . import __name__, Version

        with open(self.project.requirement_file, "w") as f:
            f.write("{}>={}\n".format(hyssop.__name__, hyssop.Version))
            f.write("{}>={}\n".format(__name__, Version))
