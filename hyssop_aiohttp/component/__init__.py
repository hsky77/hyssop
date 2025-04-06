# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: January 1st 2021

Modified By: hsky77
Last Updated: April 6th 2025 07:37:05 am
"""

from hyssop.component import ComponentTypes

from .aio_client import AioClientComponent


class AioHttpComponentTypes(ComponentTypes):
    AioClient = AioClientComponent
