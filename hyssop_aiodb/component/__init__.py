# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: December 26th 2020

Modified By: hsky77
Last Updated: June 1st 2022 12:16:18 pm
'''

from hyssop.project.component import ComponentTypes

from .aiodb_mixin import AiodbComponentMixin


class AioDBComponentTypes(ComponentTypes):
    AioDB = ('aiodb', 'aiodb', 'AioDBComponent')
