# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: January 1st 2021

Modified By: hsky77
Last Updated: January 7th 2021 15:30:08 pm
'''

from hyssop.project.component import ComponentTypes

from .aio_client import AioClientComponent


class AioHttpComponentTypes(ComponentTypes):
    AioClient = ('aioclient', 'aio_client', 'AioClientComponent')
