from importlib import import_module
from inspect import isclass
from typing import Any, Generator, Generic, List, Tuple, Type, TypeVar, get_args

from .func import join_to_abs_path

DynamicClassType = TypeVar("DynamicClassType")


class DynamicClassesTypes(Generic[DynamicClassType]):
    """Base ComponentTypes"""

    @classmethod
    def get_module_abs_path(cls) -> str:
        return join_to_abs_path(cls.get_module_path())

    @classmethod
    def get_module_path(cls) -> str:
        return cls.__module__.replace(".", "/")

    @classmethod
    def get_generic_type(cls) -> Type[DynamicClassType]:
        return get_args(cls.__orig_bases__[0])[0]  # type: ignore

    @classmethod
    def get_dynamic_classes(cls) -> Generator[Tuple[str, Type[DynamicClassType]], Any, None]:
        for k, v in cls.__dict__.items():
            if isclass(v) and issubclass(v, cls.get_generic_type()):
                yield k.lower(), v

    @classmethod
    def get_dynamic_classes_types(cls, module: str) -> List[Type["DynamicClassesTypes[DynamicClassType]"]]:
        m = import_module(module)
        return [v for v in m.__dict__.values() if isclass(v) and issubclass(v, cls) and v != cls]
