# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: September 4th 2020

Modified By: hsky77
Last Updated: January 3rd 2021 09:26:34 am
'''

from uuid import UUID
from asyncio import Lock
from types import TracebackType
from typing import Dict, List, Any, Tuple, Type, Union, Optional, AsyncGenerator
import enum
from datetime import datetime, date

from sqlalchemy.dialects.sqlite import pysqlite
from sqlalchemy.dialects.mysql import pymysql
from sqlalchemy import create_engine, Table, Column, and_
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.sql.elements import BinaryExpression, ClauseElement
from sqlalchemy.engine.result import ResultMetaData, RowProxy
from sqlalchemy.engine.interfaces import ExecutionContext
from sqlalchemy.sql.ddl import DDLElement
from sqlalchemy.sql import Insert, Update, Delete
from sqlalchemy.inspection import inspect

import aiosqlite
import aiomysql

from hyssop.util import BaseLocal

from .constants import (LocalCode_Missing_File_Path, LocalCode_Missing_Host, LocalCode_Missing_User,
                        LocalCode_No_Valid_DT_FORMAT,  LocalCode_Missing_Password, LocalCode_Missing_DB_Name,
                        LocalCode_Invalid_Column, LocalCode_Primary_Key_required, LocalCode_Not_Allow_Update)

DeclarativeBases: dict = {}


def get_declarative_base(key: str = 'default') -> DeclarativeMeta:
    """
    get entity class declarative meta class
    """
    if not key in DeclarativeBases:
        DeclarativeBases[key] = declarative_base()
    return DeclarativeBases[key]


class DATETIME_TYPE(enum.Enum):
    PY = '%Y-%m-%d %H:%M:%S.%f'
    DTF1 = '%Y-%m-%dT%H:%M:%S.%f'
    DTF2 = '%Y-%m-%d %H:%M:%S.%f'
    DTF3 = '%Y/%m/%dT%H:%M:%S.%f'
    DTF4 = '%Y/%m/%d %H:%M:%S.%f'
    DT1 = '%Y-%m-%dT%H:%M:%S'
    DT2 = '%Y-%m-%d %H:%M:%S'
    DT3 = '%Y/%m/%dT%H:%M:%S'
    DT4 = '%Y/%m/%d %H:%M:%S'
    D1 = '%Y-%m-%d'
    D2 = '%Y-%m-%d'
    D3 = '%Y/%m/%d'
    D4 = '%Y/%m/%d'

    def str_to_dt(self, sdt: str) -> datetime:
        return datetime.strptime(sdt, self.value)

    def dt_to_str(self, dt: datetime) -> str:
        return dt.strftime(self.value)


def str_to_datetime(sdt: str) -> datetime:
    """try convert str to datetime with DATETIME_TYPE format until no exception"""
    for k in DATETIME_TYPE:
        try:
            return datetime.strptime(sdt, k.value)
        except:
            pass
    raise IndexError(BaseLocal.get_message(LocalCode_No_Valid_DT_FORMAT, sdt))


def datetime_to_str(dt: datetime, dt_type: DATETIME_TYPE = DATETIME_TYPE.PY) -> str:
    return dt.strftime(dt_type.value)


PY_DT_Converter = DATETIME_TYPE.PY
DOT_NET_DT_Converter = DATETIME_TYPE.DT1


class DB_MODULE_NAME(enum.Enum):
    SQLITE_MEMORY = 'sqlite:///:memory:'
    SQLITE_FILE = 'sqlite:///{}'
    MYSQL = 'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'


def get_connection_string(db_module: DB_MODULE_NAME, **kwargs) -> str:
    connect_string = db_module.value

    if db_module == DB_MODULE_NAME.SQLITE_FILE:
        file_name = kwargs.get('file_name')
        if file_name is None:
            raise KeyError(BaseLocal.get_message(LocalCode_Missing_File_Path))
        connect_string = db_module.value.format(file_name)

    elif db_module == DB_MODULE_NAME.MYSQL:
        host = kwargs.get('host')
        if host is None:
            raise KeyError(BaseLocal.get_message(LocalCode_Missing_Host))

        user = kwargs.get('user')
        if user is None:
            raise KeyError(BaseLocal.get_message(LocalCode_Missing_User))

        password = kwargs.get('password')
        if password is None:
            raise KeyError(BaseLocal.get_message(LocalCode_Missing_Password))

        db_name = kwargs.get('db_name')
        if db_name is None:
            raise KeyError(BaseLocal.get_message(LocalCode_Missing_DB_Name))

        port = kwargs.get('port', 3306)

        connect_string = db_module.value.format(
            user, password, host, port, db_name)

    return connect_string


class SQLAlchemyEntityMixin():
    Not_Allow_Update_Columns: List[str] = []

    @classmethod
    def table(cls) -> Table:
        """Get Table object"""
        return cls.metadata.tables[cls.__tablename__]

    @classmethod
    def columns(cls) -> List[Column]:
        """Get list of column classes"""
        return inspect(cls).columns

    @classmethod
    def column_names(cls) -> List[str]:
        return [c.name for c in cls.columns()]

    @classmethod
    def primary_keys(cls) -> List[Column]:
        """Get list of primary key column classes"""
        return inspect(cls).primary_key

    @classmethod
    def primary_key_names(cls) -> List[str]:
        return [c.name for c in cls.primary_keys()]

    @classmethod
    def non_primary_keys(cls) -> List[Column]:
        """Get list of non-primary key column classes"""
        pkeys = cls.primary_keys()
        return [x for x in cls.columns() if not x in pkeys]

    @classmethod
    def non_primary_key_names(cls) -> List[str]:
        return [c.name for c in cls.non_primary_keys()]

    @classmethod
    def foreign_keys(cls) -> List[Column]:
        return {k.name: k.foreign_keys for k in [x for x in cls.columns() if x.foreign_keys]}

    @classmethod
    def relationships(cls):
        return inspect(cls).relationships.items()

    @classmethod
    def filter_key_values(cls, **kwargs) -> Dict[str, Any]:
        """Get entity values contains columns in dict"""
        column_names = [c.name for c in cls.columns()]
        return {k: v for k, v in kwargs.items() if k in column_names}

    @classmethod
    def filter_primary_key_values(cls, **kwargs) -> Dict[str, Any]:
        """Get entity values contains primary key columns in dict"""
        column_names = [c.name for c in cls.primary_keys()]
        return {k: v for k, v in kwargs.items() if k in column_names}

    @classmethod
    def filter_non_primary_key_values(cls, **kwargs) -> Dict[str, Any]:
        """Get entity values contains non-primary key columns in dict"""
        column_names = [c.name for c in cls.non_primary_keys()]
        return {k: v for k, v in kwargs.items() if k in column_names}

    @property
    def key_values(self) -> Dict[str, Any]:
        """Get entity values contains columns in dict"""
        return {k.name: getattr(self, k.name) for k in self.columns()}

    @property
    def primary_key_values(self) -> Dict[str, Any]:
        """Get entity values contains primary key columns in dict"""
        return {k.name: getattr(self, k.name) for k in self.primary_keys()}

    @property
    def non_primary_key_values(self, **kwargs) -> Dict[str, Any]:
        """Get entity values contains non-primary key columns in dict"""
        return {k.name: getattr(self, k.name) for k in self.non_primary_keys()}

    def to_json_dict(self) -> Dict[str, Any]:
        """Generate dict that is serializable by Json convertor"""
        return {k: v if not type(v) is datetime else str(v) for k, v in self.key_values.items()}

    def equals(self, right: "SQLAlchemyEntityMixin") -> bool:
        """Compare two entities"""
        if issubclass(type(right), SQLAlchemyEntityMixin):
            r = right.key_values
            l = self.key_values
            for k, v in r.items():
                if not l[k] == v:
                    return False
            return True
        return False


class CompilationContext:
    def __init__(self, context: ExecutionContext):
        self.context = context


class ClauseCompiler():
    def __init__(self, dialect):
        self._dialect = dialect

    def compile(self, query) -> Tuple[str, list, CompilationContext]:
        execution_context = self._dialect.execution_ctx_cls()
        execution_context.dialect = self._dialect

        # execute value functions
        if isinstance(query, Insert):
            execution_context.current_parameters = query.parameters
            self.set_default_value(query, execution_context)
        elif isinstance(query, Update):
            execution_context.current_parameters = query.parameters
            self.set_update_value(query, execution_context)

        compiled = query.compile(dialect=self._dialect)

        args = []

        if not isinstance(query, DDLElement):
            for key, raw_val in compiled.construct_params().items():
                if key in compiled._bind_processors:
                    val = compiled._bind_processors[key](raw_val)
                else:
                    val = raw_val
                args.append(val)

            execution_context.result_column_struct = (
                compiled._result_columns,
                compiled._ordered_columns,
                compiled._textual_ordered_columns,
            )
        return compiled.string, args, CompilationContext(execution_context)

    def set_default_value(self, clause: ClauseElement, context: ExecutionContext):
        for column in clause.table.columns:
            if not column.name in clause.parameters and column.default:
                clause.parameters[column.name] = column.default.arg(context) if callable(
                    column.default.arg) else column.default.arg

                if isinstance(clause.parameters[column.name], UUID):
                    clause.parameters[column.name] = clause.parameters[column.name].hex

    def set_update_value(self, clause: ClauseElement, context: ExecutionContext):
        for column in clause.table.columns:
            if column.onupdate and callable(column.onupdate.arg):
                clause.parameters[column.name] = column.onupdate.arg(context)


class AsyncCursorProxy():
    def __init__(self, connection_proxy: "AsyncConnectionProxy", compiler: ClauseCompiler):
        self._connection_proxy = connection_proxy
        self._compiler = compiler

    async def __aenter__(self) -> "AsyncCursorProxy":
        raise NotImplementedError()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()

    async def fetch_all(self, clause: ClauseElement) -> List[RowProxy]:
        raise NotImplementedError()

    async def fetch_many(self, clause: ClauseElement, size: int = None) -> List[RowProxy]:
        raise NotImplementedError()

    async def fetch_one(self, clause: ClauseElement) -> Optional[RowProxy]:
        raise NotImplementedError()

    async def execute(self, clause: ClauseElement) -> Any:
        raise NotImplementedError()

    async def execute_return_row(self, clause: ClauseElement) -> Optional[RowProxy]:
        raise NotImplementedError()

    async def execute_many(self, queries: List[ClauseElement]) -> None:
        raise NotImplementedError()

    async def commit(self) -> None:
        raise NotImplementedError()

    async def rollback(self) -> None:
        raise NotImplementedError()

    async def iterate(self, clause: ClauseElement) -> AsyncGenerator[RowProxy, None]:
        raise NotImplementedError()


class AioSqliteCursorProxy(AsyncCursorProxy):
    def __init__(self, connection_proxy: "AsyncConnectionProxy"):
        super().__init__(connection_proxy, ClauseCompiler(
            pysqlite.dialect(paramstyle="qmark")))

    async def __aenter__(self) -> "AioSqliteCursorProxy":
        self._cursor = await self._connection_proxy.connection.cursor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cursor.close()

    @property
    def cursor(self) -> aiosqlite.Cursor:
        return self._cursor

    async def fetch_all(self, clause: ClauseElement) -> List[RowProxy]:
        query, args, context = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        rows = await self.cursor.fetchall()
        metadata = ResultMetaData(context, self.cursor.description)
        return [RowProxy(metadata, row, metadata._processors, metadata._keymap) for row in rows]

    async def fetch_many(self, clause: ClauseElement, size: int = None) -> List[RowProxy]:
        query, args, context = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        rows = await self.cursor.fetchmany(size)
        metadata = ResultMetaData(context, self.cursor.description)
        return [RowProxy(metadata, row, metadata._processors, metadata._keymap) for row in rows]

    async def fetch_one(self, clause: ClauseElement) -> Optional[RowProxy]:
        query, args, context = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        row = await self.cursor.fetchone()
        if row is None:
            return None
        metadata = ResultMetaData(context, self.cursor.description)
        return RowProxy(metadata, row, metadata._processors, metadata._keymap)

    async def execute(self, clause: ClauseElement) -> Any:
        query, args, _ = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        return self.cursor.rowcount if self.cursor.lastrowid == 0 else self.cursor.lastrowid

    async def execute_return_row(self, clause: ClauseElement) -> Optional[RowProxy]:
        query, args, _ = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        rowid = self.cursor.rowcount if self.cursor.lastrowid == 0 else self.cursor.lastrowid

        # fetch inserted/updated row
        await self.cursor.execute('SELECT * from {} where rowid = {}'.format(clause.table.name, rowid))
        row = await self.cursor.fetchone()
        _, _, context = self._compiler.compile(clause.table.select())
        if row is None:
            return None
        metadata = ResultMetaData(context, self.cursor.description)
        return RowProxy(metadata, row, metadata._processors, metadata._keymap)

    async def execute_many(self, queries: List[ClauseElement]) -> None:
        for query in queries:
            await self.execute(query)

    async def iterate(self, clause: ClauseElement) -> AsyncGenerator[RowProxy, None]:
        query, args, context = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        metadata = ResultMetaData(context, self.cursor.description)
        row = await self.cursor.fetchone()
        while row is not None:
            yield RowProxy(metadata, row, metadata._processors, metadata._keymap)
            row = await self.cursor.fetchone()

    async def commit(self) -> None:
        await self.cursor.execute("COMMIT")

    async def rollback(self) -> None:
        await self.cursor.execute("ROLLBACK")


class AioMysqlCursorProxy(AsyncCursorProxy):
    def __init__(self, connection_proxy: "AioMysqlConnectionProxy"):
        super().__init__(connection_proxy, ClauseCompiler(
            pymysql.dialect()))

    async def __aenter__(self) -> "AioMysqlCursorProxy":
        self._cursor = await self._connection_proxy.connection.cursor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cursor.close()

    @property
    def cursor(self) -> aiomysql.Cursor:
        return self._cursor

    async def fetch_all(self, clause: ClauseElement) -> List[RowProxy]:
        query, args, context = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        rows = await self.cursor.fetchall()
        metadata = ResultMetaData(context, self.cursor.description)
        return [RowProxy(metadata, row, metadata._processors, metadata._keymap) for row in rows]

    async def fetch_many(self, clause: ClauseElement, size: int = None) -> List[RowProxy]:
        query, args, context = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        rows = await self.cursor.fetchmany(size)
        metadata = ResultMetaData(context, self.cursor.description)
        return [RowProxy(metadata, row, metadata._processors, metadata._keymap) for row in rows]

    async def fetch_one(self, clause: ClauseElement) -> Optional[RowProxy]:
        query, args, context = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        row = await self.cursor.fetchone()
        if row is None:
            return None
        metadata = ResultMetaData(context, self.cursor.description)
        return RowProxy(metadata, row, metadata._processors, metadata._keymap)

    async def execute(self, clause: ClauseElement) -> Any:
        query, args, _ = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        if self.cursor.lastrowid == 0:
            return self.cursor.rowcount
        return self.cursor.lastrowid

    async def execute_return_row(self, clause: ClauseElement) -> Optional[RowProxy]:
        query, args, _ = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        rowid = self.cursor.rowcount if self.cursor.lastrowid == 0 else self.cursor.lastrowid

        # fetch inserted/updated row
        await self.cursor.execute('SELECT * from {} where rowid = {}'.format(clause.table.name, rowid))
        row = await self.cursor.fetchone()
        _, _, context = self._compiler.compile(clause.table.select())
        if row is None:
            return None
        metadata = ResultMetaData(context, self.cursor.description)
        return RowProxy(metadata, row, metadata._processors, metadata._keymap)

    async def execute_many(self, queries: List[ClauseElement]) -> None:
        for query in queries:
            await self.execute(query)

    async def iterate(self, clause: ClauseElement) -> AsyncGenerator[RowProxy, None]:
        query, args, context = self._compiler.compile(clause)
        await self.cursor.execute(query, args)
        metadata = ResultMetaData(context, self.cursor.description)
        row = await self.cursor.fetchone()
        while row is not None:
            yield RowProxy(metadata, row, metadata._processors, metadata._keymap)
            row = await self.cursor.fetchone()

    async def commit(self) -> None:
        await self.cursor.execute("COMMIT")

    async def rollback(self) -> None:
        await self.cursor.execute("ROLLBACK")


class AsyncConnectionProxy():
    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self,
                        exc_type: Type[BaseException] = None,
                        exc_value: BaseException = None,
                        traceback: TracebackType = None,
                        ) -> None:
        self.release()

    async def dispose(self):
        raise NotImplementedError()

    async def acquire(self):
        raise NotImplementedError()

    async def get_cursor_proxy(self) -> AsyncCursorProxy:
        raise NotImplementedError()

    def release(self):
        raise NotImplementedError()


class AioMysqlConnectionProxy(AsyncConnectionProxy):
    def __init__(self,
                 host: str, port: int, user: str, password: str, db_name: str):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self._is_connected = False
        self._lock = Lock()

    @property
    def locked(self) -> bool:
        return self._lock.locked()

    @property
    def connection(self) -> aiomysql.Connection:
        return self._conn

    def get_cursor_proxy(self) -> AioMysqlCursorProxy:
        return AioMysqlCursorProxy(self)

    async def dispose(self):
        await self.acquire(False)
        self._conn.close()
        self.release()

    async def acquire(self, ping: bool = True):
        await self._lock.acquire()
        if not self._is_connected:
            self._is_connected = True
            self._conn = await aiomysql.connect(
                self.host, self.user, self.password, self.db_name, self.port)
        if ping and self._conn:
            await self._conn.ping()

    def release(self):
        self._lock.release()


class AioSqliteConnectionProxy(AsyncConnectionProxy):
    def __init__(self, file_name: str):
        super().__init__()
        self._lock = Lock()
        self._conn = aiosqlite.connect(file_name)
        self._is_connected = False

    @property
    def connection(self) -> aiosqlite.Connection:
        return self._conn

    @property
    def locked(self) -> bool:
        return self._lock.locked()

    def get_cursor_proxy(self) -> AioSqliteCursorProxy:
        return AioSqliteCursorProxy(self)

    async def acquire(self):
        await self._lock.acquire()
        if not self._is_connected:
            self._is_connected = True
            await self._conn

    def release(self):
        self._lock.release()

    async def dispose(self):
        await self.acquire()
        await self._conn.close()
        self.release()


class AsyncSQLAlchemyRDB():
    def __init__(self, db_module: DB_MODULE_NAME,
                 declared_entity_base: DeclarativeBases,
                 connect_args: Dict = {},
                 engine_args: Dict = {},
                 **kwargs):
        self.engine = create_engine(get_connection_string(
            db_module, **kwargs), connect_args=connect_args, **engine_args)
        self.declared_entity_base = declared_entity_base
        self.declared_entity_base.metadata.create_all(self.engine)

    def get_connection_proxy(self) -> AsyncConnectionProxy:
        raise NotImplementedError()

    async def dispose(self):
        raise NotImplementedError()


class AioMySQLDatabase(AsyncSQLAlchemyRDB):
    def __init__(self,
                 declared_entity_base: DeclarativeBases,
                 connect_args: Dict = {},
                 engine_args: Dict = {},
                 **kwargs):
        super().__init__(DB_MODULE_NAME.MYSQL, declared_entity_base, connect_args,
                         engine_args, **kwargs)
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.user = kwargs['user']
        self.password = kwargs['password']
        self.db_name = kwargs['db_name']

        self.connection_proxy = AioMysqlConnectionProxy(
            self.host, self.port, self.user, self.password, self.db_name)

    def get_connection_proxy(self) -> AioMysqlConnectionProxy:
        return self.connection_proxy

    async def dispose(self):
        await self.connection_proxy.dispose()


class AioSqliteDatabase(AsyncSQLAlchemyRDB):
    def __init__(self,
                 declared_entity_base: DeclarativeBases,
                 connect_args: Dict = {},
                 engine_args: Dict = {},
                 **kwargs):
        super().__init__(DB_MODULE_NAME.SQLITE_FILE, declared_entity_base, connect_args,
                         engine_args, **kwargs)
        self.connection_proxy = AioSqliteConnectionProxy(
            kwargs['file_name'])

    def get_connection_proxy(self) -> AioSqliteConnectionProxy:
        return self.connection_proxy

    async def dispose(self):
        await self.connection_proxy.dispose()


Async_Uw_Mapper: Dict[SQLAlchemyEntityMixin, "AsyncEntityUW"] = {}


class AsyncEntityUW():
    def __init__(self, entity_cls: SQLAlchemyEntityMixin):
        self._entity_cls = entity_cls
        Async_Uw_Mapper[self._entity_cls] = self

    @property
    def table(self):
        return self._entity_cls.table()

    @property
    def foreign_keys(self):
        return self._entity_cls.foreign_keys()

    @property
    def relationships(self):
        return self._entity_cls.relationships()

    def convert_value_type(self, **kwargs):
        for column in self._entity_cls.columns():
            if column.name in kwargs:
                kwargs[column.name] = self.value_type_convert(
                    column.type.python_type, kwargs[column.name])
        return kwargs

    def value_type_convert(self, t: type, v: Any):
        if isinstance(v, t):
            return v
        elif t is datetime:
            return str_to_datetime(v)
        elif t is date:
            return str_to_datetime(v).date()
        elif issubclass(t, enum.IntEnum):
            return t(int(v))
        else:
            return t(v)

    def column_clause(self, cursor: AsyncCursorProxy, column_objs=None, **kwargs) -> Union[None, BinaryExpression]:
        """Get where column clasuse for select entity"""
        columns = column_objs if column_objs else self._entity_cls.columns()
        clause = None
        for p in columns:
            if p.name in kwargs:
                if clause is not None:
                    clause = and_(clause, p == self.value_type_convert(
                        p.type.python_type, kwargs[p.name]))
                else:
                    clause = p == self.value_type_convert(
                        p.type.python_type, kwargs[p.name])
        return clause

    def primary_key_clause(self, cursor: AsyncCursorProxy, **kwargs) -> Union[None, BinaryExpression]:
        """Get identity columns clasuse for selecting entity"""
        return self.column_clause(cursor, self._entity_cls.primary_keys(), **kwargs)

    def non_primary_key_clause(self, cursor: AsyncCursorProxy, **kwargs) -> Union[None, BinaryExpression]:
        """Get non identity columns clasuse for selecting entity"""
        return self.column_clause(cursor, self._entity_cls.non_primary_keys(), **kwargs)

    # functions
    async def select(self, cursor: AsyncCursorProxy, **kwargs) -> List[SQLAlchemyEntityMixin]:
        """Select database with or without keys and return a list of entities"""
        if len(kwargs) > 0:
            rows = await cursor.fetch_all(self._entity_cls.table().select().where(self.column_clause(cursor, **kwargs)))
        else:
            rows = await cursor.fetch_all(self._entity_cls.table().select())
        return [self._entity_cls(**dict(row.items())) for row in rows]

    async def load(self, cursor: AsyncCursorProxy, **kwargs) -> SQLAlchemyEntityMixin:
        """Select database with keys, and return first matched entity"""
        if len(kwargs) > 0:
            row = await cursor.fetch_one(self._entity_cls.table().select().where(self.column_clause(cursor, **kwargs)))
        else:
            row = await cursor.fetch_one(self._entity_cls.table().select())
        return self._entity_cls(**dict(row.items())) if row else None

    async def delete(self, cursor: AsyncCursorProxy, entities: List[SQLAlchemyEntityMixin]) -> None:
        """Delete a list of entities from database"""
        for entity in entities:
            await cursor.execute(self._entity_cls.table().delete().where(self.primary_key_clause(cursor, **entity.key_values)))

    async def add(self, cursor: AsyncCursorProxy, **kwargs) -> SQLAlchemyEntityMixin:
        """Insert one entity"""
        kwargs = self.convert_value_type(**kwargs)

        row = await cursor.execute_return_row(self._entity_cls.table().insert().values(**kwargs))
        return self._entity_cls(**dict(row.items())) if row else None

    async def merge(self, cursor: AsyncCursorProxy, **kwargs) -> SQLAlchemyEntityMixin:
        """Insert or replace one entity."""
        pks = self._entity_cls.filter_primary_key_values(**kwargs)
        if len(pks) > 0:
            entity = await self.load(cursor, **pks)
            if entity:
                entity = await self.update(cursor, entity, **self._entity_cls.filter_non_primary_key_values(**kwargs))
            else:
                entity = await self.add(cursor, **kwargs)
            return entity
        else:
            entity = await self.add(cursor, **kwargs)
            return entity

    async def update(self, cursor: AsyncCursorProxy, entity: SQLAlchemyEntityMixin, **kwargs) -> SQLAlchemyEntityMixin:
        """Update entity non primary key values"""
        if entity and len(kwargs) > 0:
            self._check_allow_to_update(kwargs)
            kwargs = self.convert_value_type(**kwargs)

            npks = entity.non_primary_key_values
            for k, v in kwargs.items():
                if k in npks:
                    if isinstance(getattr(entity, k), datetime):
                        if isinstance(v, str):
                            setattr(entity, k, str_to_datetime(v))
                        else:
                            setattr(entity, k, v)
                    else:
                        setattr(entity, k, v)
                else:
                    raise RuntimeError(LocalCode_Invalid_Column, k)

            await cursor.execute(entity.table().update().where(self.primary_key_clause(cursor, **entity.key_values)).values(**entity.key_values))
            return await self.load(cursor, **entity.primary_key_values)

    def _check_allow_to_update(self, kwargs):
        for k in kwargs:
            if k in self._entity_cls.Not_Allow_Update_Columns:
                raise KeyError(BaseLocal.get_message(
                    LocalCode_Not_Allow_Update, k))

    # async def delete_relationship_entity(self, cursor: AsyncCursorProxy, entity: SQLAlchemyEntityMixin, target_property_name: str = None):
    #     dt = entity.relationships()
    #     for k, v in dt:
    #         uw = Async_Uw_Mapper[v.entity.class_]
    #         entities = []
    #         if target_property_name:
    #             if target_property_name == k:
    #                 if v.uselist:
    #                     entities = await self._select_relationship_entity(db, entity, v.entity.class_)
    #                 else:
    #                     e = await self._load_relationship_entity(db, entity, v.entity.class_)
    #                     if e:
    #                         entities.append(e)
    #         else:
    #             if v.uselist:
    #                 entities = await self._select_relationship_entity(db, entity, v.entity.class_)
    #             else:
    #                 e = await self._load_relationship_entity(db, entity, v.entity.class_)
    #                 if e:
    #                     entities.append(e)

    #         await uw.delete(db, entities)

    # async def include(self, cursor: AsyncCursorProxy, entity: SQLAlchemyEntityMixin, target_property_name: str = None) -> None:
    #     """Load relation entity of 1st level"""
    #     dt = entity.relationships()
    #     for k, v in dt:
    #         if target_property_name:
    #             if target_property_name == k:
    #                 setattr(entity, k, await self._select_relationship_entity(cursor, entity, v.entity.class_) if v.uselist
    #                         else await self._load_relationship_entity(cursor, entity, v.entity.class_))
    #         else:
    #             setattr(entity, k, await self._select_relationship_entity(cursor, entity, v.entity.class_) if v.uselist
    #                     else await self._load_relationship_entity(cursor, entity, v.entity.class_))

    # async def _load_relationship_entity(self, cursor: AsyncCursorProxy, entity: SQLAlchemyEntityMixin, related_entity_type: SQLAlchemyEntityMixin):
    #     uw = Async_Uw_Mapper[related_entity_type]
    #     kv = {}
    #     for fkey, fvalue in uw.foreign_keys.items():
    #         for fk in fvalue:
    #             for column in entity.columns():
    #                 if fk.column.anon_label == column.anon_label:
    #                     kv[column.name] = getattr(entity, column.name)
    #                     break
    #     return await uw.load(cursor, **kv)

    # async def _select_relationship_entity(self, cursor: AsyncCursorProxy, entity: SQLAlchemyEntityMixin, related_entity_type: SQLAlchemyEntityMixin):
    #     uw = Async_Uw_Mapper[related_entity_type]
    #     kv = {}
    #     for fkey, fvalue in uw.foreign_keys.items():
    #         for fk in fvalue:
    #             for column in entity.columns():
    #                 if fk.column.anon_label == column.anon_label:
    #                     kv[column.name] = getattr(entity, column.name)
    #                     break
    #     return await uw.select(cursor, **kv)

    # async
    # def relationship_merge(self, cursor: AsyncCursorProxy, parent: SQLAlchemyEntityMixin, name: str, child: SQLAlchemyEntityMixin):
    #     """
    #     append entity to relationship field
    #     """
    #     f = getattr(parent, name)
    #     if not child in f:
    #         f.append(child)

    # def relationship_remove(self, cursor: AsyncCursorProxy, parent: SQLAlchemyEntityMixin, name: str, child: SQLAlchemyEntityMixin):
    #     """
    #     remove entity from relationship field
    #     """
    #     f = getattr(parent, name)
    #     if child in f:
    #         f.remove(child)
