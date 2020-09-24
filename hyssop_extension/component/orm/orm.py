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
                    connections: <int>                   # optional - db access worker limit, default 1

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
Last Updated: September 24th 2020 21:00:21 pm
'''

import logging

from typing import Callable, Dict, Any

from hyssop.util import join_path, BaseLocal
from hyssop.web.component import Component, ComponentManager, add_module_default_logger

from .utils import DB_MODULE_NAME, DeclarativeMeta
from .entity import IUnitOfWork, BasicUW
from .executor_pool import OrmExecutorFactory, OrmExecutor
from .constants import LocalCode_Not_Support_DB_Module


class OrmDBComponent(Component):
    """
    Component for managing sql database access with server config
    """

    default_loggers = ['sqlalchemy', 'sqlalchemy.orm.mapper.Mapper']

    support_db_type = ['sqlite', 'sqlite_memory', 'mysql']

    def init(self, component_manager: ComponentManager, **kwargs) -> None:
        self.root_dir = kwargs.get('root_dir', '')
        self._disposed = False

        self.dbs = {k: v for k, v in kwargs.items() if not 'root_dir' in k}
        for k in self.dbs:
            self.dbs[k]['db'] = None
            self.dbs[k]['connections'] = self.dbs[k].get('connections', 1)

            if not self.dbs[k]['module'] in self.support_db_type:
                raise ValueError(BaseLocal.get_message(
                    LocalCode_Not_Support_DB_Module, k, self.dbs[k]['module']))

            if self.dbs[k]['module'] == 'sqlite':
                self.dbs[k]['file_name'] = join_path(
                    self.root_dir, self.dbs[k]['file_name'])
            elif self.dbs[k]['module'] == 'mysql':
                self.dbs[k]['']

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
                db = OrmExecutorFactory(db_id, self.dbs[db_id]['connections'])

                module = DB_MODULE_NAME.SQLITE_MEMORY
                if self.dbs[db_id]['module'] == 'sqlite':
                    module = DB_MODULE_NAME.SQLITE_FILE
                elif self.dbs[db_id]['module'] == 'mysql':
                    module = DB_MODULE_NAME.MYSQL

                db.set_engine(db.get_connection_string(
                    module, **self.dbs[db_id]), declared_entity_base)
                self.dbs[db_id]['db'] = db

    def get_executor(self, db_id: str, unit_of_work: IUnitOfWork = BasicUW) -> OrmExecutor:
        if db_id in self.dbs:
            return self.dbs[db_id]['db'].get_executor(unit_of_work=unit_of_work)
        raise KeyError('no key')

    def dispose(self, component_manager: ComponentManager) -> None:
        self._disposed = True
        for db_id in self.dbs:
            self.dbs[db_id]['db'].dispose()


# add sqlalchemy logger as the default logger in logger component
add_module_default_logger(OrmDBComponent.default_loggers)

for name in OrmDBComponent.default_loggers:
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
