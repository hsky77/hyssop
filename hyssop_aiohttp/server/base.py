from typing import TypeVar
from aiohttp.web_routedef import _Deco
from hyssop.utils.dynamic_class_types import DynamicClassesTypes


class ControllerTypes(DynamicClassesTypes[_Deco]):
    """Basic Controller types"""

    pass


ControllerType = TypeVar("ControllerType", bound=_Deco)
