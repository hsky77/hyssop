# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


"""
File created: August 21st 2020

This module contains the "yaml" configurable component classes for hyssop application.

    - to create Project components:

        0. the hierarchy of folders and files looks like:

            server_directory/
                server_config.yaml
                component/
                    __init__.py
                    foo.py

        1. use ComponentTypes enum class to define the extend components such as:

            class ComponentExtension(ComponentTypes):
                # tuple(<component_key>, <package_route>, <class_name_in_the_py_file>)

                Foo = ('foo', 'foo', 'Foo')

        2. in "foo.py" contains the class code:

            from hyssop.project.component import Component, ComponentManager
            from . import ComponentExtension

            class Foo(Component):
                def __init__(self):
                    super().__init__(ComponentExtension.Foo)

                def init(self, component_manager: ComponentManager, p1, *arugs, **kwargs) -> None:
                    self.p1 = p1

        3. setup component block of "server_config.yaml" to tell hyssop server load the extend components "Foo":

            component:              # block to setup component
                foo:                # component_key to load
                    p1: xxxx        # parameter p1 of Foo.init()

Modified By: hsky77
Last Updated: April 3rd 2025 10:08:01 am
"""


from os import getcwd
from typing import Any, Dict, List, Type, TypeVar

from hyssop.component.base import ComponentManager, ComponentTypes, Component
from hyssop.component.localization import LocalizationComponent
from hyssop.component.logger import LoggerComponent
from hyssop.utils import join_path
from hyssop.utils.dynamic_class_types import DynamicClassesTypes


class DefaultComponentTypes(ComponentTypes):
    """server loads all components of this enum type when start"""

    Localization = LocalizationComponent
    Logger = LoggerComponent


class DefaultComponentManager(ComponentManager):

    def get_message(self, code: int, *args):
        comp = self.get_component(LocalizationComponent)
        return comp.get_message(code, *args)

    def get_logger(self, name: str):
        comp = self.get_component(LoggerComponent)
        return comp.get_logger(name)


ComponentManagerT = TypeVar("ComponentManagerT", bound=ComponentManager)

default_component_module_paths: List[str] = ["hyssop.component"]


def create_component_manager(
    project_dir: str = getcwd(),
    component_settings: Dict[str, Any] = {},
    default_module_paths: List[str] = default_component_module_paths,
    extended_component_module_paths: List[str] = [],
    component_manager_t: Type[ComponentManagerT] = DefaultComponentManager,
) -> ComponentManagerT:
    """Example of component_module_path: hyssop.component"""
    default_component_types: List[Type[DynamicClassesTypes[Component]]] = []
    for path in default_module_paths:
        default_component_types += ComponentTypes.get_dynamic_classes_types(path)
    ext_comp_types: List[Type[DynamicClassesTypes[Component]]] = []
    for path in extended_component_module_paths:
        ext_comp_types += ComponentTypes.get_dynamic_classes_types(join_path(path))
    component_manager = component_manager_t(*default_component_types + ext_comp_types)  # type: ignore

    # set default component instances
    for component_types in default_component_types:
        for name, component_type in component_types.get_dynamic_classes():
            component_type.name = name
            component_manager.set_component(
                component_type,
                component_type.get_generic_type().model_validate(component_settings.pop(component_type.name, {})),
                project_dir,
            )

    for component in component_manager.components:
        component.init()

    # create non-default component instances
    if component_settings is not None:
        for component_name, data in component_settings.items():
            component_manager.set_component(component_name, data, project_dir=project_dir)

        # call component init()
        for component_name, _ in component_settings.items():
            comp = component_manager.get_component(component_name)
            comp.init()

    return component_manager


def add_module_default_logger(logger_names: List[str]) -> None:
    LoggerComponent.default_loggers = LoggerComponent.default_loggers + logger_names


def add_default_component_types(module_path: str):
    default_component_module_paths.append(module_path)
