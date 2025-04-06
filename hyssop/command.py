# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: August 21st 2020

Modified By: hsky77
Last Updated: April 4th 2025 16:54:20 pm
"""

import os
import argparse

from . import Version
from .utils.func import join_path, join_to_abs_path
from .project import HyssopProject
from . import Module_Path


class CommandProcessor:
    Command_Test_Project = "test"
    Command_Create_Project = "create"
    Command_Show_Version = "version"
    Command_Pack_Project = "pack"

    args_key_project_directory = "project_directory"

    def __init__(self):
        self.project_dir = Module_Path
        self.__create_command_parser()

    def process_command(self):
        self.__parse_command()

        if hasattr(self.args, "command"):
            if hasattr(self, self.args.command):
                func = getattr(self, self.args.command)
                if callable(func):
                    func()
                else:
                    self.parser.print_help()
        else:
            self.parser.print_help()

    def test(self):
        import unittest

        # import coverage

        project = HyssopProject(self.project_dir)
        runner = unittest.TextTestRunner()
        # cov = coverage.Coverage()
        # cov.start()
        runner.run(project.cretae_test_suite())
        # cov.stop()
        # cov.save()
        # cov.report()
        # cov.html_report(directory="htmlcov")

    def pack(self) -> None:
        from .project.pack import HyssopPack

        if self.project_dir:
            HyssopPack().pack(
                self.project_dir,
                self.args.o,
                prepare_wheels=self.args.add_wheels,
                compile_py=not self.args.decompile_pyc,
            )

    def version(self):
        print("hyssop {}".format(Version))

    def create(self):
        self.project_dir = self.project_dir if self.project_dir else "hello_world"
        self.project = HyssopProject(self.project_dir)

        if not os.path.isdir(self.project_dir):
            os.makedirs(self.project_dir)

        self._create_project_component_files()
        self._create_project_controller_files()
        self._create_project_config_files()
        self._create_project_test_files()
        self._create_project_pack_files()
        self._create_project_requirement_files()

        print("project created at", os.path.abspath(self.project_dir))

    def _create_project_component_files(self):
        if not os.path.isdir(self.project.component_dir):
            os.makedirs(self.project.component_dir)

        with open(join_path(self.project.component_dir, "__init__.py"), "w") as f:
            f.write(
                """\
from hyssop.component import ComponentTypes
from .hello import HelloComponent


class HelloComponentTypes(ComponentTypes):
    Hello = HelloComponent
"""
            )

        with open(join_path(self.project.component_dir, "hello.py"), "w") as f:
            f.write(
                """\
from pydantic import BaseModel, Field

from hyssop.component import Component


class HelloComponentConfig(BaseModel):
    p1: str = Field(..., description="p1 is required and string type")


class HelloComponent(Component[HelloComponentConfig]):
    def hello(self) -> str:
        return f"init Hello component load from {__package__} and the parameters p1: {self.config.p1}"
"""
            )

    def _create_project_controller_files(self):
        pass

    def _create_project_test_files(self):
        if not os.path.isdir(self.project.unitetest_dir):
            os.makedirs(self.project.unitetest_dir)

        with open(join_path(self.project.unitetest_dir, "__init__.py"), "w") as f:
            f.write(
                """\
from hyssop.unit_test import UnitTestTypes

from .ut1 import UT1TestCase


class UTTypes(UnitTestTypes):
    UT1 = UT1TestCase
"""
            )

        with open(join_path(self.project.unitetest_dir, "ut1.py"), "w") as f:
            f.write(
                """\
import os

from hello.component import HelloComponentTypes
from hyssop.project import HyssopProject
from hyssop.unit_test.base import IUnitTestCase


class UT1TestCase(IUnitTestCase):
    def test(self):
        path = os.path.dirname(os.path.dirname(__file__))
        config = {
            "component": {
                "hello": {"p1": "This is p1"},
            }
        }
        project = HyssopProject(path, config)
        component_manager = project.create_component_manager()
        comp = component_manager.get_component(HelloComponentTypes.Hello)
        assert comp.hello() is not None
"""
            )

    def _create_project_config_files(self):
        with open(self.project.config_file, "w") as f:
            f.write(
                """\
name: hyssop Project
debug: False
component:
  hello:
    p1: 'This is p1'
"""
            )

    def _create_project_pack_files(self):
        with open(self.project.pack_file, "w") as f:
            f.write(
                """
# This is packing list indicated what are the files should be pack
# If this file does not exist under the project folder, all of the files under the folder will be packed

include:
# List absolute or relative path of additional file or directory to be packed
# - example.txt
# - example_dir

exclude:
# List absolute or relative path of file, directory, or file extension to be ignored.
- '.log'
"""
            )

    def _create_project_requirement_files(self):
        # requirement
        from . import __name__, Version

        with open(self.project.requirement_file, "w") as f:
            f.write("{}>={}".format(__name__, Version))

    def __create_command_parser(self):
        self.parser = argparse.ArgumentParser(prog="hyssop")
        self.command_parsers = self.parser.add_subparsers(title="command")

        test_parser = self.command_parsers.add_parser(
            CommandProcessor.Command_Test_Project, help="test hyssop library or specfied project directory path"
        )
        test_parser.add_argument(self.args_key_project_directory, nargs="?", help="project directory path")
        test_parser.set_defaults(command=CommandProcessor.Command_Test_Project)

        make_serv_parser = self.command_parsers.add_parser(
            CommandProcessor.Command_Create_Project,
            help="create a project template with specfied project directory path",
        )
        make_serv_parser.add_argument(self.args_key_project_directory, help="project directory path")
        make_serv_parser.set_defaults(command=CommandProcessor.Command_Create_Project)

        pack_parser = self.command_parsers.add_parser(
            CommandProcessor.Command_Pack_Project, help="pack project with specfied project directory path"
        )
        pack_parser.add_argument(self.args_key_project_directory, help="project directory path")
        pack_parser.add_argument("-o", help="specify output compressed file path", default=None)
        pack_parser.add_argument("-w", "--add_wheels", action="store_true", help="add dependency wheel files")
        pack_parser.add_argument("-d", "--decompile_pyc", action="store_true", help="disable compile .py to .pyc")
        pack_parser.set_defaults(command=CommandProcessor.Command_Pack_Project)

        version_serv_parser = self.command_parsers.add_parser(
            CommandProcessor.Command_Show_Version, help="print version number to console"
        )
        version_serv_parser.set_defaults(command=CommandProcessor.Command_Show_Version)

    def __parse_command(self):
        self.args = self.parser.parse_args()
        if hasattr(self.args, self.args_key_project_directory):
            attr = getattr(self.args, self.args_key_project_directory)
            if attr is not None:
                self.project_dir = join_to_abs_path(attr)
