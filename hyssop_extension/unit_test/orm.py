# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: September 4th 2020

Modified By: hsky77
Last Updated: September 24th 2020 21:00:51 pm
'''

import sys
import unittest
import asyncio
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import Session

from hyssop.unit_test import UnitTestCase, UnitTestServer
from hyssop.web.component import create_server_component_manager, DefaultComponentTypes

from component import WebConfigComponentValidator, HyssopExtensionComponentTypes
from component.orm import (Entity, OrmExecutor, OrmExecutorFactory, EntityMixin,
                           get_declarative_base, BasicUW, DB_MODULE_NAME, get_session_maker,
                           PY_DT_Converter, DOT_NET_DT_Converter, str_to_datetime, OrmDBComponent)


DeclarativeBase = get_declarative_base()


class GenderType(enum.Enum):
    Male = 'male'
    Female = 'female'


class TestEntity(DeclarativeBase, EntityMixin):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum(GenderType), nullable=False)
    secret = Column(String(40))
    note = Column(String(100))
    schedule = Column(DateTime, default=datetime.now)


TestUW = BasicUW(TestEntity)


class OrmTestCase(UnitTestCase):
    def test(self):
        self.test_component()
        self.test_dt()
        self.test_orm()
        self.test_orm_factory()

    def test_component(self):
        component_setting = {
            'orm':
            {
                'db_1': {
                    'module': 'sqlite_memory',
                    'connections': 1
                }
            }
        }
        UnitTestServer.validate_config(component_setting)

        component_manager = create_server_component_manager(
            component_setting, sys.path[0])

        component_manager.invoke(
            DefaultComponentTypes.Logger, 'update_default_logger', False)

        orm: OrmDBComponent = component_manager.get_component(
            HyssopExtensionComponentTypes.OrmDB)

        orm.init_db_declarative_base('db_1', DeclarativeBase)

        with orm.get_executor('db_1', TestUW) as executor:
            entity = executor.add(name='someone', age=50,
                                  gender=GenderType.Female, secret='my secret', note='this is note')

            self.assertIsNotNone(entity)
            self.assertEqual(entity.name, 'someone')
            self.assertEqual(entity.age, 50)
            self.assertEqual(entity.gender, GenderType.Female)
            self.assertEqual(entity.secret, 'my secret')
            self.assertEqual(entity.note, 'this is note')

            executor.commit()

        orm.dispose(component_manager)

    def test_dt(self):
        now = datetime.now().replace(microsecond=0)
        self.assertEqual(now, PY_DT_Converter.str_to_dt(
            PY_DT_Converter.dt_to_str(now)))

        self.assertEqual(now, DOT_NET_DT_Converter.str_to_dt(
            DOT_NET_DT_Converter.dt_to_str(now)))

        py_time = '2019-07-07 16:34:22'
        dnet_time = '2019-07-07T16:34:22'
        self.assertEqual(str_to_datetime(py_time),
                         datetime(2019, 7, 7, 16, 34, 22))
        self.assertEqual(str_to_datetime(dnet_time),
                         datetime(2019, 7, 7, 16, 34, 22))

    def test_orm(self):
        sess = get_session_maker(
            DB_MODULE_NAME.SQLITE_MEMORY, DeclarativeBase)()
        self.assertIsInstance(sess, Session)

        entity = TestUW.add(sess, name='someone', age=30,
                            gender=GenderType.Male, secret='my secret', note='this is note')

        self.assertEqual(entity.name, 'someone')
        self.assertEqual(entity.age, 30)
        self.assertEqual(entity.gender, GenderType.Male)
        self.assertEqual(entity.secret, 'my secret')
        self.assertEqual(entity.note, 'this is note')

        TestUW.commit(sess)
        TestUW.refresh(sess, entity)
        TestUW.update(sess, entity, age=50, gender=GenderType.Female)

        self.assertEqual(entity.name, 'someone')
        self.assertEqual(entity.age, 50)
        self.assertEqual(entity.gender, GenderType.Female)
        self.assertEqual(entity.secret, 'my secret')
        self.assertEqual(entity.note, 'this is note')

        try:
            TestUW.update(sess, entity, name='sometwo')
        except:
            self.assertEqual(entity.name, 'someone')
            TestUW.rollback(sess)
            TestUW.refresh(sess, entity)

        self.assertTrue('secret' in entity.key_values)
        sess.close()

    def test_orm_factory(self):
        executor_factory = OrmExecutorFactory(connections=1)
        executor_factory.set_engine(executor_factory.get_connection_string(
            DB_MODULE_NAME.SQLITE_MEMORY), DeclarativeBase)

        try:
            self.do_test_factory(executor_factory)
            self.test_async_heavy_access(executor_factory)
        finally:
            executor_factory.dispose()

    def test_async_heavy_access(self, executor_factory: OrmExecutorFactory):
        async def test_async(index: int):
            async with executor_factory.get_executor(TestUW) as executor:
                # await executor.reserve_session_async()
                entity = await executor.load_async(id=1)

                self.assertIsNotNone(entity)
                self.assertEqual(entity.age, 50)
                self.assertEqual(entity.gender, GenderType.Female)
                self.assertEqual(entity.secret, 'my secret')
                self.assertEqual(entity.note, 'this is note')

        futures = []
        count = 300
        for i in range(count):
            futures.append(asyncio.ensure_future(test_async(i)))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(futures))

    def do_test_factory(self, executor_factory: OrmExecutorFactory):
        with executor_factory.get_executor(TestUW) as executor:
            entity = executor.add(name='someone', age=50,
                                  gender=GenderType.Female, secret='my secret', note='this is note')

            self.assertIsNotNone(entity)
            self.assertEqual(entity.name, 'someone')
            self.assertEqual(entity.age, 50)
            self.assertEqual(entity.gender, GenderType.Female)
            self.assertEqual(entity.secret, 'my secret')
            self.assertEqual(entity.note, 'this is note')

            executor.commit()

        async def test_db_async():
            entity = await executor_factory.run_method_async(TestUW.add, name='someone', age=50,
                                                             gender=GenderType.Male, secret='my secret', note='this is note')

            self.assertIsNotNone(entity)
            self.assertEqual(entity.name, 'someone')
            self.assertEqual(entity.age, 50)
            self.assertEqual(entity.gender, GenderType.Male)
            self.assertEqual(entity.secret, 'my secret')
            self.assertEqual(entity.note, 'this is note')

            await executor_factory.run_method_async(TestUW.rollback)

            async with executor_factory.get_executor(TestUW) as executor:
                entity = await executor.add_async(name='someone', age=50,
                                                  gender=GenderType.Female, secret='my secret', note='this is note')

                self.assertIsNotNone(entity)
                self.assertEqual(entity.name, 'someone')
                self.assertEqual(entity.age, 50)
                self.assertEqual(entity.gender, GenderType.Female)
                self.assertEqual(entity.secret, 'my secret')
                self.assertEqual(entity.note, 'this is note')
                await executor.commit_async()

            with executor_factory.get_executor(TestUW) as executor:
                try:
                    entity = executor.load(id=1)
                    executor.update(entity, age=18)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 18)
                    self.assertEqual(entity.gender, GenderType.Female)
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')
                    executor.flush()
                    raise Exception('test')
                except:
                    executor.rollback()
                    executor.refresh(entity)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 50)
                    self.assertEqual(entity.gender, GenderType.Female)
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')

            async with executor_factory.get_executor(TestUW) as executor:
                try:
                    entity = await executor.load_async(name='someone')

                    self.assertIsNotNone(entity)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 50)
                    self.assertEqual(entity.gender, GenderType.Female)
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')

                    await executor.update(entity, age=18)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 18)
                    self.assertEqual(entity.gender, GenderType.Female)
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')

                    await executor.flush_async()
                except:
                    await executor.rollback_async()
                    await executor.refresh_async(entity)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 50)
                    self.assertEqual(entity.gender, GenderType.Female)
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')

        entity = executor_factory.run_method(TestUW.add, name='someone', age=50,
                                             gender=GenderType.Male, secret='my secret', note='this is note')

        self.assertIsNotNone(entity)
        self.assertEqual(entity.name, 'someone')
        self.assertEqual(entity.age, 50)
        self.assertEqual(entity.gender, GenderType.Male)
        self.assertEqual(entity.secret, 'my secret')
        self.assertEqual(entity.note, 'this is note')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_db_async())
