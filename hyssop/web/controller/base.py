# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

This module defines the base controller classes

Modified By: hsky77
Last Updated: August 27th 2020 12:31:57 pm
'''

from typing import Callable, Any, List

from tornado.web import RequestHandler

from ...util import DynamicTypeEnum
from .. import Controller_Module_Folder


class ControllerType(DynamicTypeEnum):
    """base abstract controller enum class"""
    @staticmethod
    def get_controller_enum_class() -> List[DynamicTypeEnum]:
        try:
            return DynamicTypeEnum.get_dynamic_class_enum_class(Controller_Module_Folder)
        except:
            pass

    def import_class(self):
        return super().import_class(cls_type=RequestHandler)
