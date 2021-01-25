# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: September 4th 2020

    OrmDBComponent:

        - managing sql database connection and access with server config as followings:

        note:
            OrmDBComponent holds database connection, database might cut off the connections for long time idles,
            so it's necessary to refresh connection by calling reset_session() or reset_session_async() before query database,
            parameter "connection_refresh" is the timer to prevent rapidly reconnect database

        component:                                  # component block of server_config.yaml
            orm:                                    # indicate OrmDB Component
                db_id_1:    <str>                   # define string id will be use in code
                    module: <str>                   # required - support 'sqlite', 'sqlite_memory', 'mysql'
                    connections: <int>                   # optional - db access worker limit, default 5

                    # when module is 'sqlite', you should add parameters:
                    file_name: <str>                # required - specify sqlite db file path

                    # when module is 'mysql', you should add parameters:
                    host:       <str>               # required - db ip
                    port:       <int>               # required - db port
                    db_name:    <str>               # required - db database name
                    user:       <str>               # required - login user id
                    password:   <str>               # required - login user password
                db_id_2:
                    ...etc

Modified By: hsky77
Last Updated: January 24th 2021 15:55:49 pm
'''

import logging

from typing import Callable, Dict, Any, Union

from hyssop.util import join_path, BaseLocal
from hyssop.project.component import Component, ComponentManager, add_module_default_logger

from .utils import DB_MODULE_NAME, DeclarativeMeta, AsyncSQLAlchemyRDB, AioMySQLDatabase, AioSqliteDatabase
from .constants import LocalCode_Not_Support_DB_Module


class AioDBComponent(Component):
    """
    Component for managing sql database access with server config
    """

    default_loggers = ['sqlalchemy',
                       'sqlalchemy.orm.mapper.Mapper',
                       'sqlalchemy.orm.strategies.LazyLoader',
                       'sqlalchemy.orm.relationships.RelationshipProperty',
                       'sqlalchemy.engine.base.Engine']

    support_db_type = ['sqlite', 'mysql']

    def init(self, component_manager: ComponentManager, **kwargs) -> None:
        self.project_dir = kwargs.get('project_dir', '')
        self._disposed = False

        self.dbs = {k: v for k, v in kwargs.items() if not 'project_dir' in k}
        for k in self.dbs:
            self.dbs[k]['db'] = None

            if not self.dbs[k]['module'] in self.support_db_type:
                raise ValueError(BaseLocal.get_message(
                    LocalCode_Not_Support_DB_Module, k, self.dbs[k]['module']))

            if self.dbs[k]['module'] == 'sqlite':
                self.dbs[k]['file_name'] = join_path(
                    self.project_dir, self.dbs[k]['file_name'])

    def info(self) -> Dict:
        res = {}
        for db_id in self.dbs:
            res[db_id] = self.get_db_settings(db_id)
        return {**super().info(), **{'info': res}}

    def get_db_settings(self, db_id: str) -> Dict:
        return {k: v for k, v in self.dbs[db_id].items() if not k in ['db']}

    def init_db_declarative_base(self, db_id: str, declared_entity_base: DeclarativeMeta) -> None:
        if db_id in self.dbs:
            if not self.dbs[db_id]['db']:
                if self.dbs[db_id]['module'] == 'sqlite':
                    self.dbs[db_id]['db'] = AioSqliteDatabase(
                        declared_entity_base, **self.dbs[db_id])
                elif self.dbs[db_id]['module'] == 'mysql':
                    self.dbs[db_id]['db'] = AioMySQLDatabase(
                        declared_entity_base, **self.dbs[db_id])

    def get_async_database(self, db_id: str) -> Union[None, AsyncSQLAlchemyRDB]:
        return self.dbs[db_id]['db']

    async def dispose(self, component_manager: ComponentManager) -> None:
        self._disposed = True
        for db_id in self.dbs:
            if self.dbs[db_id]['db']:
                await self.dbs[db_id]['db'].dispose()


# add sqlalchemy logger as the default logger in logger component
add_module_default_logger(AioDBComponent.default_loggers)

for name in AioDBComponent.default_loggers:
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
