# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: August 21st 2020

provide basic python unittest.TestSuite of the following test cases:
    - hyssop.util, worker, and executor
    - hyssop.project.web config validation, components and controllers

use get_test_suite() to get the default or extend test suite by inheriting "hyssop.unit_test.UnitTestTypes."

Usage:
    - to create unit_test extension module:

        0. the hierarchy of folders and files looks like:

            server_directory/
                server_config.yaml
                unit_test/
                    __init__.py
                    foo.py

        1. "foo.py" defines class FooTestCase:

            from hyssop.unit_test import UnitTestCase

            class FooTestCase(UnitTestCase):
                # override this test method
                def test(self):
                    # test modules...

        2. "__init__.py" defines the enum class allows load the test case classes dynamically,

            from hyssop.unit_test import UnitTestTypes

            class ExTestTypes(UnitTestTypes):
                FooTest = ('foo_test', 'foo', 'FooTestCase')

        3. In the commond prompt, run command "python -m hyssop test <server_directory>"
            to test all the extend test cases defined in "__init__.py"

Modified By: hsky77
Last Updated: April 4th 2025 17:15:07 pm
"""

from typing import Optional
from unittest import TestSuite

from .base import UnitTestTypes
from .ut_project import TestCaseComponent
from .ut_worker import TestCaseWorker


class DefaultUnitTestTypes(UnitTestTypes):
    TestComponent = TestCaseComponent
    TestWorker = TestCaseWorker


def get_test_suite(unittest_module_path: Optional[str] = __package__) -> TestSuite:
    """
    get test suite of unittest module.
    It will try to load extend test suite if specifed in server folder "unit_test", elsewise default test suite.
    Default test suite tests util and web modules of hyssop
    """

    suite = TestSuite()
    if unittest_module_path is None:
        raise ValueError("unittest_module_path is not specified")
    types = UnitTestTypes.get_dynamic_classes_types(unittest_module_path)
    for t in types:
        for _, test_cls in t.get_dynamic_classes():
            suite.addTest(test_cls("test"))
    return suite
