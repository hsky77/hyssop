# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: August 21st 2020

Modified By: hsky77
Last Updated: April 4th 2025 17:16:11 pm
"""

from asyncio import run
from logging import DEBUG


from .base import IUnitTestCase


class TestCaseComponent(IUnitTestCase):
    def test(self):
        from hyssop import Module_Path
        from hyssop.project import HyssopProject
        from hyssop.component.constants import LocalCode_Hello

        config = {
            "name": "hyssop project unit test",
            "component": {
                "localization": {"lang": "en", "dir": "component"},
                "logger": {
                    "log_level": DEBUG,
                    "log_to_console": True,
                },
            },
        }

        project = HyssopProject(Module_Path, config)
        component_manager = project.create_component_manager()
        component_manager.get_logger("unit test").debug(component_manager.get_message(LocalCode_Hello))
        run(component_manager.dispose_components())
