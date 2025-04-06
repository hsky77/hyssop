# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: August 21st 2020

This module defines the base component classes

Modified By: hsky77
Last Updated: April 3rd 2025 10:07:37 am
"""


from inspect import isclass, iscoroutinefunction, ismethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, get_args, overload
from pydantic import BaseModel

from hyssop.utils import BaseLocal
from hyssop.utils.dynamic_class_types import DynamicClassesTypes

from .constants import LocalCode_Component_Duplicated_Key, LocalCode_Component_Type_Not_Exist, LocalCode_Not_Subclass

ComponentConfig = TypeVar("ComponentConfig", bound=BaseModel)


class Component(Generic[ComponentConfig]):
    """Base component interface defines the callbacks of componet life cycle."""

    name: str = "component"

    def __init__(
        self, component_manager: "ComponentManager", config: ComponentConfig, project_dir: Optional[str] = None
    ):
        self.component_manager = component_manager
        self.project_dir = project_dir
        self.config = config

    @classmethod
    def get_generic_type(cls) -> Type[BaseModel]:
        return get_args(cls.__orig_bases__[0])[0]  # type: ignore

    def init(self):
        """Called when component_manager create component objects"""
        pass

    async def start(self):
        """Called when component_manager start component objects in coroutine."""
        pass

    def info(self) -> Dict[str, Any]:
        """Return metadata of this component."""
        return {"config": self.config.model_dump()}

    async def dispose(self):
        """Called when component_manager dispose component objects"""
        pass


class ComponentTypes(DynamicClassesTypes[Component]):
    """Basic component types"""

    pass


ComponentType = TypeVar("ComponentType", bound=Component)


class ComponentManager:
    """Class to store and manage components."""

    def __init__(self, *component_types: DynamicClassesTypes[ComponentType]):
        self.__components: Dict[str, Component] = {}
        self.__component_classes: List[Type[Component]] = []
        for types in component_types:
            for name, component_class in types.get_dynamic_classes():
                component_class.name = name
                self.__component_classes.append(component_class)

        self.__component_classes_in_disposing_order = self.__component_classes[::-1]

    @property
    def component_classes(self) -> List[Type[Component]]:
        return self.__component_classes

    @property
    def component_classes_in_disposing_order(self) -> List[Type[Component]]:
        return self.__component_classes_in_disposing_order

    @property
    def components(self) -> List[Component]:
        return [v for v in self.__components.values()]

    @property
    def info(self) -> Dict[str, Any]:
        info = {}
        for component in self.components:
            info[component.name] = component.info()
        return info

    async def start_components(self):
        """Start components."""
        for component_cls in self.component_classes:
            comp = self._get_component(component_cls.name)
            if comp is not None:
                if iscoroutinefunction(comp.start):
                    await comp.start()
                elif ismethod(comp.start):
                    comp.start()

    async def dispose_components(self):
        """Dispose components."""
        for component_cls in self.component_classes_in_disposing_order:
            comp = self._get_component(component_cls.name)
            if comp is not None:
                if iscoroutinefunction(comp.dispose):
                    await comp.dispose()
                elif ismethod(comp.dispose):
                    comp.dispose()

    @overload
    def set_component(
        self,
        component: Type[ComponentType],
        config: Optional[ComponentConfig] = None,
        project_dir: Optional[str] = None,
        replace: bool = False,
    ):
        """Add component object."""
        ...

    @overload
    def set_component(
        self,
        component: str,
        config: Optional[Dict[str, Any]] = None,
        project_dir: Optional[str] = None,
        replace: bool = False,
    ):
        """Add component object."""
        ...

    def set_component(
        self,
        component,
        config=None,
        project_dir: Optional[str] = None,
        replace: bool = False,
    ):
        """Add component object."""
        if not replace and self.has_component(component):
            raise KeyError(BaseLocal.get_message(LocalCode_Component_Duplicated_Key, component))

        if isinstance(component, str):
            component = next((x for x in self.__component_classes if x.name == component.lower()), None)
            if component is not None:
                config = component.get_generic_type().model_validate(config)

        if isclass(component) and issubclass(component, Component):
            comp = component(self, config, project_dir)
            self.__components[comp.name] = comp
            return
        raise TypeError(BaseLocal.get_message(LocalCode_Not_Subclass, component, Component))

    @overload
    def get_component(self, component: Type[ComponentType]) -> ComponentType:
        """Return stored component object."""
        ...

    @overload
    def get_component(self, component: str) -> Component:
        """Return stored component object."""
        ...

    def get_component(self, component) -> Component:
        """Return stored component object."""
        comp = self._get_component(component)
        if comp is None:
            raise KeyError(BaseLocal.get_message(LocalCode_Component_Type_Not_Exist, component))
        return comp

    @overload
    def has_component(self, component: Type[ComponentType]) -> bool:
        """Contain stored component object"""
        ...

    @overload
    def has_component(self, component: str) -> bool:
        """Contain stored component object"""
        ...

    def has_component(self, component) -> bool:
        """Contain stored component object"""
        return self._get_component(component) is not None

    @overload
    def _get_component(self, component: Type[ComponentType]) -> Optional[ComponentType]:
        """Return stored component object."""
        ...

    @overload
    def _get_component(self, component: str) -> Optional[Component]:
        """Return stored component object."""
        ...

    def _get_component(self, component: Any) -> Optional[Component]:
        """Return stored component object."""
        if isinstance(component, str):
            return self.__components.get(component)
        elif isclass(component):
            if not issubclass(component, Component):
                raise TypeError(BaseLocal.get_message(LocalCode_Not_Subclass, type(component), Component))
            return next((v for v in self.__components.values() if isinstance(v, component)), None)
