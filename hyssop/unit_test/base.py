# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: August 21st 2020

Modified By: hsky77
Last Updated: April 4th 2025 16:57:35 pm
"""

from abc import ABC, abstractmethod
from unittest import TestCase

from hyssop.utils.dynamic_class_types import DynamicClassesTypes

Unittest_Module_Folder = "unit_test"


class IUnitTestCase(ABC, TestCase):
    """hyssop unittest case interface"""

    @abstractmethod
    def test(self):
        pass


class UnitTestTypes(DynamicClassesTypes[IUnitTestCase]):
    """Base unit test types."""
