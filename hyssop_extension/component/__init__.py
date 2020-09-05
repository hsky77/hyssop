# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: September 4th 2020

Modified By: hsky77
Last Updated: September 4th 2020 17:49:45 pm
'''

from hyssop.web.component import ComponentTypes
from hyssop.web.config_validator import (WebConfigComponentValidator, ConfigContainerMeta,
                                         ConfigElementMeta, ConfigScalableContainerMeta, ConfigSwitchableElementMeta)

WebConfigComponentValidator.set_cls_parameters(
    ConfigContainerMeta(
        'orm_db', False,
        ConfigScalableContainerMeta(
            str,
            ConfigSwitchableElementMeta(
                'module', str, True,
                ConfigContainerMeta(
                    'sqlite_memory', False,
                    ConfigElementMeta('connections', int, True)
                ),
                ConfigContainerMeta(
                    'sqlite', False,
                    ConfigElementMeta('connections', int, True),
                    ConfigElementMeta('file_name', str, True)
                ),
                ConfigContainerMeta(
                    'mysql', False,
                    ConfigElementMeta('connections', int, True),
                    ConfigElementMeta('host', str, True),
                    ConfigElementMeta('port', int, True),
                    ConfigElementMeta('db_name', str, True),
                    ConfigElementMeta('user', str, True),
                    ConfigElementMeta('password', str, True)
                ),
            )
        )
    )
)


class HyssopExtensionComponentTypes(ComponentTypes):
    """server loads configured components of this enum type when start"""
    OrmDB = ('orm_db', 'orm', 'OrmDBComponent')
