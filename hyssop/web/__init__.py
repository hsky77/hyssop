# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: August 27th 2020 13:10:16 pm
'''


from .constants import *
from ..util import BaseLocal, join_path

BaseLocal.import_csv([join_path(__path__[0], Localization_File)])
