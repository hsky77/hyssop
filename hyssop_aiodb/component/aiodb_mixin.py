# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: June 1st 2022

Modified By: hsky77
Last Updated: June 1st 2022 12:15:49 pm
'''

from functools import wraps
from hyssop_aiodb.component.aiodb.utils import DeclarativeMeta


class AiodbComponentMixin():
    def init(self,
             component_manager,
             db_id: str,
             DB_MODULES: DeclarativeMeta,
             *arugs,
             aiodb_component_key: str = 'aiodb',
             **kwargs) -> None:
        self.db_comp = component_manager.get_component(aiodb_component_key)
        self.db_id = db_id
        self.db_comp.init_db_declarative_base(self.db_id, DB_MODULES)
        self.async_db = self.db_comp.get_async_database(self.db_id)

    def db_access(dispatch_func):
        @wraps(dispatch_func)
        async def inner(self, *args, **kwargs):
            async with self.async_db.get_connection_proxy() as conn:
                async with conn.get_cursor_proxy() as cursor:
                    return await dispatch_func(self, cursor, *args, **kwargs)

        return inner
