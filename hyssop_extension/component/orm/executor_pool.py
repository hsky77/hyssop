# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: September 4th 2020

Modified By: hsky77
Last Updated: September 17th 2020 15:53:51 pm
'''

import time
import asyncio
import inspect
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Tuple

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.exc import DBAPIError

from hyssop.util import ExecutorFactory, Executor, FunctionQueueWorker, BaseLocal

from .utils import DB_MODULE_NAME, get_connection_string
from .entity import IUnitOfWork, BasicUW, Entity
from .constants import (LocalCode_Missing_File_Path, LocalCode_Missing_Host, LocalCode_Missing_User,
                        LocalCode_Is_Not_Sub_Type, LocalCode_Method_Is_Not_Belong_To_Class,
                        LocalCode_Missing_Password, LocalCode_Missing_DB_Name)


class _OrmDBConnector():
    def __init__(self,
                 engine: Engine,
                 declared_entity_base: DeclarativeMeta,
                 **kwargs):
        self._engine = engine
        self._declared_entity_base = declared_entity_base
        self.session = None
        self._maker = None
        self._schema_created = False
        self._connect_exception = None
        self._failed_time = None
        self._session_lock = None

        self._reconnect_interval = kwargs.get('reconnect_interval', 5)
        self._autoflush = kwargs.get('autoflush', False)

    @property
    def is_connected(self) -> bool:
        return not self._maker == None

    def accquire(self, executor) -> None:
        while self._session_lock:
            time.sleep(0)

        self._session_lock = executor

    async def accquire_async(self, executor) -> None:
        while self._session_lock:
            await asyncio.sleep(0)

        self._session_lock = executor

    def release(self, executor) -> None:
        if executor is self._session_lock:
            self._session_lock = None

    def connect(self):
        if not self._maker:
            if self._connect_exception and self._failed_time:
                if datetime.now() - self._failed_time < self._reconnect_interval:
                    self._connect_exception = None
                    self._failed_time = None

            if not self._failed_time:
                try:
                    if not self._schema_created:
                        self._declared_entity_base.metadata.create_all(
                            self._engine)
                        self._schema_created = True

                    self._maker = sessionmaker(
                        bind=self._engine, autoflush=self._autoflush, expire_on_commit=False)
                except Exception as e:
                    self._failed_time = datetime.now()
                    self._connect_exception = e
                    raise e from e

        if self._connect_exception:
            raise self._connect_exception from self._connect_exception

    def create_session(self):
        self.session = self._maker()

    def close_session(self):
        if self.session:
            self.session.close()


class OrmExecutor(Executor):
    def __init__(self,
                 worker: FunctionQueueWorker,
                 engine: Engine,
                 declared_entity_base: DeclarativeMeta,
                 unit_of_work: IUnitOfWork = BasicUW,
                 **kwargs):
        super().__init__(worker)

        if not hasattr(self.worker, 'connector'):
            self.worker.connector = _OrmDBConnector(
                engine, declared_entity_base, **kwargs)

        self.connector: _OrmDBConnector = self.worker.connector
        self.uw = unit_of_work

    def __enter__(self):
        self.create_session()
        return self

    def __exit__(self, type, value, traceback):
        self.cancel_reservation()

    async def __aenter__(self):
        await self.create_session_async()
        return self

    async def __aexit__(self, type, value, traceback):
        self.cancel_reservation()

    def create_session(self):
        if not self.connector.is_connected:
            super().run_method(self.connector.connect)

        if not self.connector.session:
            super().run_method(self.connector.create_session)

    async def create_session_async(self):
        if not self.connector.is_connected:
            await super().run_method_async(self.connector.connect)

        if not self.connector.session:
            await super().run_method_async(self.connector.create_session)

    def close_session(self):
        super().run_method(self.connector.close_session)

    async def close_session_async(self):
        await super().run_method_async(self.connector.close_session)

    def reserve_session(self):
        self.connector.accquire(self)

    async def reserve_session_async(self):
        await self.connector.accquire_async(self)

    def cancel_reservation(self):
        self.connector.release(self)

    def execute(self, func, *args, **kwargs):
        if issubclass(type(self.uw), IUnitOfWork):
            try:
                return super().run_method(func, self.connector.session, *args, **kwargs)
            except DBAPIError as e:
                self.close_session()
                raise e from e
        else:
            raise TypeError(BaseLocal.get_message(
                LocalCode_Is_Not_Sub_Type, type(self.uw), IUnitOfWork))

    async def execute_async(self, func, *args, **kwargs):
        if issubclass(type(self.uw), IUnitOfWork):
            try:
                return await super().run_method_async(func, self.connector.session, *args, **kwargs)
            except DBAPIError as e:
                await self.close_session_async()
                raise e from e
        else:
            raise TypeError(BaseLocal.get_message(
                LocalCode_Is_Not_Sub_Type, type(self.uw), IUnitOfWork))

    def run_method_in_queue(self,
                            func: Callable,
                            *args,
                            on_finish: Callable[[Any], None] = None,
                            on_exception: Callable[[Exception], None] = None,
                            **kwargs) -> None:
        """Execute the given func in queue. This method does not block the calling thread"""
        super().run_method_in_queue(func, self.connector.session,
                                    *args, on_finish, on_exception, **kwargs)

    def run_method(self,
                   func: Callable,
                   **kwargs) -> Any:
        """
        Execute the given func.

        Note: This method blocks the calling thread
        """
        return super().run_method(func, self.connector.session, **kwargs)

    async def run_method_async(self,
                               func: Callable,
                               *args,
                               **kwargs) -> Any:
        """Asynchronously execute the given func."""
        return await super().run_method_async(func, self.connector.session, **kwargs)

    def select(self, **kwargs) -> List[Entity]:
        """
        Select database with or without keys and return a list of entities.
        """
        return self.execute(self.uw.select, **kwargs)

    async def select_async(self, **kwargs) -> List[Entity]:
        """
        Select database with or without keys and return a list of entities.
        """
        return await self.execute_async(self.uw.select, **kwargs)

    def load(self, **kwargs) -> Entity:
        """
        Select database with or without keys, and return first matched entity.
        """
        return self.execute(self.uw.load, **kwargs)

    async def load_async(self, **kwargs) -> Entity:
        """
        Select database with or without keys, and return first matched entity.
        """
        return await self.execute_async(self.uw.load, **kwargs)

    def delete(self, entities: List[Entity], **kwargs) -> None:
        """
        Delete a list of entities from database.
        """
        return self.execute(self.uw.delete, entities, **kwargs)

    async def delete_async(self, entities: List[Entity], **kwargs) -> None:
        """
        Delete a list of entities from database.
        """
        return await self.execute_async(self.uw.delete, entities, **kwargs)

    def add(self, **kwargs) -> Entity:
        """
        Insert one entity. Raise exception if it exists.
        """
        return self.execute(self.uw.add, **kwargs)

    async def add_async(self, **kwargs) -> Entity:
        """
        Insert one entity. Raise exception if it exists.
        """
        return await self.execute_async(self.uw.add, **kwargs)

    def merge(self, **kwargs) -> Entity:
        """
        Insert or replace one entity.
        """
        return self.execute(self.uw.merge, **kwargs)

    async def merge_async(self, **kwargs) -> Entity:
        """
        Insert or replace one entity.
        """
        return await self.execute_async(self.uw.merge, **kwargs)

    def update(self, entity: Entity, **kwargs) -> None:
        """
        Update entity values.
        """
        return self.execute(self.uw.update, entity, **kwargs)

    async def update_async(self, entity: Entity, **kwargs) -> None:
        """
        Update entity values.
        """
        return await self.execute_async(self.uw.update, entity, **kwargs)

    def relationship_merge(self, parent: Entity, name: str, child: Entity):
        """
        append entity to relationship field
        """
        return self.execute(self.uw.relationship_merge, parent, name, child)

    async def relationship_merge_async(self, parent: Entity, name: str, child: Entity):
        """
        append entity to relationship field
        """
        return await self.execute_async(self.uw.relationship_merge, parent, name, child)

    def relationship_remove(self, parent: Entity, name: str, child: Entity):
        """
        remove entity from relationship field
        """
        return self.execute(self.uw.relationship_remove, parent, name, child)

    async def relationship_remove_async(self, parent: Entity, name: str, child: Entity):
        """
        remove entity from relationship field
        """
        return await self.execute_async(self.uw.relationship_remove, parent, name, child)

    def validate(self, entity: Entity, raise_exception: bool = True) -> bool:
        """
        Validate entity column values.
        """
        return self.execute(self.uw.validate, entity, raise_exception=raise_exception)

    async def validate_async(self, entity: Entity, raise_exception: bool = True) -> bool:
        """
        Validate entity column values.
        """
        return await self.execute_async(self.uw.validate, entity, raise_exception=raise_exception)

    def refresh(self, entity: Entity) -> Entity:
        """
        Refresh entity from database.
        """
        return self.execute(self.uw.refresh, entity)

    async def refresh_async(self, entity: Entity) -> Entity:
        """
        Refresh entity from database.
        """
        return await self.execute_async(self.uw.refresh, entity)

    def flush(self) -> Tuple[int, int, int]:
        """
        Flush the session of database connection. Return changes (new, updated, deleted)
        """
        return self.execute(self.uw.flush)

    async def flush_async(self) -> Tuple[int, int, int]:
        """
        Flush the session of database connection. Return changes (new, updated, deleted)
        """
        return await self.execute_async(self.uw.flush)

    def rollback(self) -> None:
        """
        Rollback the session of database connection.
        """
        return self.execute(self.uw.rollback)

    async def rollback_async(self) -> None:
        """
        Rollback the session of database connection.
        """
        return await self.execute_async(self.uw.rollback)

    def commit(self) -> Tuple[int, int, int]:
        """
        Commit the changes to the database. Return changes (new, updated, deleted)
        """
        return self.execute(self.uw.commit)

    async def commit_async(self) -> Tuple[int, int, int]:
        """
        Commit the changes to the database. Return changes (new, updated, deleted)
        """
        return await self.execute_async(self.uw.commit)


class OrmExecutorFactory(ExecutorFactory):
    def __init__(self,
                 pool_name: str = None,
                 connections: int = 5,
                 executor_type: Executor = OrmExecutor):
        super().__init__(pool_name, executor_type, worker_limit=connections)

    def dispose(self):
        if not self._disposed:
            self._disposed = True
            for w in self.workers:
                w.run_method(w.connector.close_session)
                while w.pending_count > 0:
                    time.sleep(0)
                w.dispose()

    def get_connection_string(self, db_module: DB_MODULE_NAME, **kwargs):
        return get_connection_string(db_module, **kwargs)

    def set_engine(self,
                   connection_string: str,
                   declared_entity_base: DeclarativeMeta,
                   autoflush: bool = False,
                   reconnect_interval: int = 5,
                   *args,
                   **kwargs) -> None:
        self.declared_entity_base = declared_entity_base
        self.autoflush = autoflush
        self.reconnect_interval = reconnect_interval
        self._engine = create_engine(
            connection_string, *args, **kwargs)

    def run_method_in_queue(self,
                            func: Callable,
                            *args,
                            on_finish: Callable[[Any], None] = None,
                            on_exception: Callable[[Exception], None] = None,
                            **kwargs) -> None:
        """Execute the given func in queue. This method does not block the calling thread"""
        with self.get_executor(self.__get_UW_class(func)) as executor:
            executor.run_method_in_queue(
                func, *args, on_finish=on_finish, on_exception=on_exception, **kwargs)

    def run_method(self,
                   func: Callable,
                   *args,
                   **kwargs) -> Any:
        """
        Execute the given func. 

        Note: This method blocks the calling thread
        """
        with self.get_executor(self.__get_UW_class(func)) as executor:
            return executor.run_method(func, *args, **kwargs)

    async def run_method_async(self,
                               func: Callable,
                               *args,
                               **kwargs) -> Any:
        """Asynchronously execute the given func."""
        async with self.get_executor(self.__get_UW_class(func)) as executor:
            return await executor.run_method_async(func, *args, **kwargs)

    def get_executor(self, unit_of_work: IUnitOfWork) -> OrmExecutor:
        """
        Create and return an executor instance.
        """
        return super().get_executor(
            declared_entity_base=self.declared_entity_base,
            autoflush=self.autoflush,
            unit_of_work=unit_of_work,
            engine=self._engine,
            reconnect_interval=self.reconnect_interval)

    def __get_UW_class(self, method: Callable) -> type:
        if inspect.ismethod(method):
            for cls in inspect.getmro(method.__self__.__class__):
                if method.__name__ in cls.__dict__:
                    return cls
        if inspect.isfunction(method):
            return getattr(inspect.getmodule(method),
                           method.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])

        raise TypeError(BaseLocal.get_message(
            LocalCode_Method_Is_Not_Belong_To_Class, method))
