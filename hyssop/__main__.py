# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: September 5th 2020 20:56:18 pm
'''

import os
import sys
from .util import get_class, join_path
from . import Module_Path, Version


def start_server(server_dir: str, cmdline_args) -> None:
    from .util import get_class

    try:
        route = server_dir + '.server'
        cls = server_dir + '_server'
        server_cls = get_class(route, cls)
    except:
        from .web.server import HyssopServer
        server_cls = HyssopServer

    server = server_cls()
    server.init(server_dir, cmdline_args.http_server)
    server.start()


def pack_server(server_dir: str, cmdline_args) -> None:
    from .web.pack import HyssopPack
    HyssopPack().pack(server_dir, cmdline_args.o,
                      prepare_wheels=cmdline_args.add_wheels,
                      compile_py=not cmdline_args.decompile_pyc)


def test_server():
    import unittest
    from .unit_test import get_test_suite
    runner = unittest.TextTestRunner()
    runner.run(get_test_suite())


def create_server_folder(server_dir: str = 'hello_world'):
    from .web import (Component_Module_Folder,
                      Controller_Module_Folder,
                      Unittest_Module_Folder,
                      Hyssop_Web_Config_File,
                      Hyssop_Web_Pack_File,
                      Component_Module_Folder,
                      Controller_Module_Folder,
                      Hyssop_Web_Requirement_File)
    from .web.server import HyssopServer

    if not os.path.isdir(server_dir):
        os.makedirs(server_dir)

    # create hello component
    comp_dir = join_path(server_dir, Component_Module_Folder)
    if not os.path.isdir(comp_dir):
        os.makedirs(comp_dir)

    with open(join_path(comp_dir, '__init__.py'), 'w') as f:
        f.write('''\
from hyssop.web.component import ComponentTypes

from hyssop.web.config_validator import ConfigContainerMeta, ConfigElementMeta, WebConfigComponentValidator

# add hello validator to component config validator
WebConfigComponentValidator.set_cls_parameters(
    ConfigContainerMeta('hello', False,
        ConfigElementMeta('p1', str, True) # validate HelloComponent's 'p1' argument is required and string type
    )
)

class HelloComponentTypes(ComponentTypes):
    Hello = ('hello', 'hello', 'HelloComponent')
''')

    with open(join_path(comp_dir, 'hello.py'), 'w') as f:
        f.write('''\
from hyssop.web.component import Component
from . import HelloComponentTypes

class HelloComponent(Component):
    def init(self, component_manager, p1, *arugs, **kwargs) -> None:
        print('init Hello component load from', __package__, 'and the parameters p1:', p1)

    def hello(self):
        return 'Hello World, This is hyssop generate hello component'
''')

    # create hello controller
    controller_dir = join_path(server_dir, Controller_Module_Folder)
    if not os.path.isdir(controller_dir):
        os.makedirs(controller_dir)

    with open(join_path(controller_dir, '__init__.py'), 'w') as f:
        f.write('''\
from hyssop.web.controller import ControllerType

class HelloControllerTypes(ControllerType):
    HelloController = ('hello_world', 'hello', 'HelloController')
    THelloController = ('tornado_hello_world', 'hello', 'HelloTornadoHandler')
''')

    with open(join_path(controller_dir, 'hello.py'), 'w') as f:
        f.write('''\
from hyssop.web.controller.tornado import RequestController

from component import HelloComponentTypes

class HelloController(RequestController):
    async def get(self):
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

        hello_comp = self.component_manager.get_component(HelloComponentTypes.Hello)
        self.write(hello_comp.hello())

from tornado.web import RequestHandler

class HelloTornadoHandler(RequestHandler):
    async def get(self):
        """
        ---
        tags:
        - tornado hello
        summary: hello world get
        description: simple test controller
        produces:
        - text/html
        responses:
            200:
              description: return hello message
        """        

        hello_comp = self.application.component_manager.get_component(HelloComponentTypes.Hello)
        self.write(hello_comp.hello())
''')

    # unit test
    ut_dir = join_path(server_dir, Unittest_Module_Folder)
    if not os.path.isdir(ut_dir):
        os.makedirs(ut_dir)

    with open(join_path(ut_dir, '__init__.py'), 'w') as f:
        f.write('''\
from hyssop.unit_test import UnitTestTypes

class UTTypes(UnitTestTypes):
    UT1 = ('ut1', 'ut1', 'UT1TestCase')
''')

    with open(join_path(ut_dir, 'ut1.py'), 'w') as f:
        f.write('''\
from hyssop.unit_test import UnitTestCase

class UT1TestCase(UnitTestCase):
    def test(self):
        # implement unit test here...
        
        print('ut1 test case runned')
''')

    # config
    with open(join_path(server_dir, Hyssop_Web_Config_File), 'w') as f:
        f.write('''\
name: hyssop Server
port: 8888
debug: False
doc:
  description: hello api
component:
  hello: 
    p1: 'This is p1'
controller:
  /hello:
    enum: hello_world
  /hello_tornado:
    enum: tornado_hello_world
''')

    # pack
    with open(join_path(server_dir, Hyssop_Web_Pack_File), 'w') as f:
        f.write('''
# This is packing list indicated what are the files should be pack
# If this file does not exist under the project folder, all of the files under the folder will be packed

include:
# List absolute or relative path of additional file or directory to be packed
# - example.txt
# - example_dir

exclude:
# List absolute or relative path of file, directory, or file extension to be ignored.
- '.log'
''')

    # requirement
    from . import __name__, Version
    with open(join_path(server_dir, Hyssop_Web_Requirement_File), 'w') as f:
        f.write('{}>={}'.format(__name__, Version))

    print('project created at', os.path.abspath(server_dir))


Command_Start_Server = 'start'
Command_Pack_Server = 'pack'
Command_Test_Server = 'test'
Command_Create_Project = 'create'
Command_Show_Version = 'version'


def get_command_parser():
    import argparse
    parser = argparse.ArgumentParser(prog='hyssop')
    sub_parsers = parser.add_subparsers(title='command')

    start_parser = sub_parsers.add_parser(
        Command_Start_Server, help='start server with specfied server project directory path')
    start_parser.add_argument('server_directory',
                              help='server project directory path')
    start_parser.add_argument('-s', '--http_server', action='store_true',
                              help='start application on tornado http server')
    start_parser.set_defaults(command=Command_Start_Server)

    pack_parser = sub_parsers.add_parser(
        Command_Pack_Server, help='pack server with specfied server project directory path')
    pack_parser.add_argument('server_directory',
                             help='server project directory path')
    pack_parser.add_argument(
        '-o', help='specify output compressed file path', default=None)
    pack_parser.add_argument('-w', '--add_wheels', action='store_true',
                             help='add dependency wheel files')
    pack_parser.add_argument('-d', '--decompile_pyc', action='store_true',
                             help='disable compile .py to .pyc')
    pack_parser.set_defaults(command=Command_Pack_Server)

    test_parser = sub_parsers.add_parser(
        Command_Test_Server, help='test hyssop library or specfied server project directory path')
    test_parser.add_argument('server_directory', nargs='?',
                             help='server project directory path')
    test_parser.set_defaults(command=Command_Test_Server)

    make_serv_parser = sub_parsers.add_parser(
        Command_Create_Project, help='create a server template with specfied server project directory path')
    make_serv_parser.add_argument('server_directory',
                                  help='server project directory path')
    make_serv_parser.set_defaults(command=Command_Create_Project)

    version_serv_parser = sub_parsers.add_parser(
        Command_Show_Version, help='print version number to console')
    version_serv_parser.set_defaults(command=Command_Show_Version)

    return parser


def _init_server_package(server_dir: str) -> None:
    if server_dir is not None:
        if (not join_path(Module_Path) in server_dir and
                not os.path.dirname(os.path.abspath(server_dir)) in sys.path):
            sys.path.insert(0, os.path.dirname(os.path.abspath(server_dir)))

        if not join_path(Module_Path) in server_dir and not server_dir in sys.path:
            sys.path.insert(0, os.path.abspath(server_dir))

        from .util import get_class
        from .web import Component_Module_Folder, Controller_Module_Folder, Unittest_Module_Folder
        try:
            get_class(Component_Module_Folder)
        except:
            pass

        try:
            get_class(Controller_Module_Folder)
        except:
            pass

        try:
            get_class(Unittest_Module_Folder)
        except:
            pass


if __name__ == '__main__':
    parser = get_command_parser()
    args = parser.parse_args()

    if hasattr(args, 'command'):
        if args.command == Command_Start_Server:
            server_dir = args.server_directory
            _init_server_package(server_dir)
            start_server(server_dir, args)
        elif args.command == Command_Pack_Server:
            from .util import join_to_abs_path
            pack_server(join_to_abs_path(args.server_directory), args)
        elif args.command == Command_Test_Server:
            server_dir = args.server_directory
            _init_server_package(server_dir)
            test_server()
        elif args.command == Command_Create_Project:
            create_server_folder(args.server_directory)
        elif args.command == Command_Show_Version:
            print('hyssop {}'.format(Version))
        else:
            parser.print_help()
    else:
        parser.print_help()
