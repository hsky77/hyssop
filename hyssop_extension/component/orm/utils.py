# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: September 4th 2020

Modified By: hsky77
Last Updated: September 4th 2020 17:49:21 pm
'''

from typing import Dict
from enum import Enum
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.engine import Engine

from hyssop.util import BaseLocal

from .constants import (LocalCode_Missing_File_Path, LocalCode_Missing_Host, LocalCode_Missing_User,
                        LocalCode_No_Valid_DT_FORMAT,  LocalCode_Missing_Password, LocalCode_Missing_DB_Name)


class DATETIME_TYPE(Enum):
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


class DB_MODULE_NAME(Enum):
    SQLITE_MEMORY = 'sqlite:///:memory:'
    SQLITE_FILE = 'sqlite:///{}'
    MYSQL = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'


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


def get_engine(db_module: DB_MODULE_NAME,
               declared_entity_base: DeclarativeMeta,
               autoflush: bool = False,
               connect_args: Dict = {},
               engine_args: Dict = {},
               **kwargs) -> Session:
    return create_engine(get_connection_string(
        db_module, **kwargs), connect_args=connect_args, **engine_args)


def get_session_maker(db_module: DB_MODULE_NAME,
                      declared_entity_base: DeclarativeMeta,
                      autoflush: bool = False,
                      connect_args: Dict = {},
                      engine_args: Dict = {},
                      **kwargs) -> Session:
    engine = create_engine(get_connection_string(
        db_module, **kwargs), connect_args=connect_args, **engine_args)
    declared_entity_base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=autoflush, expire_on_commit=False)
