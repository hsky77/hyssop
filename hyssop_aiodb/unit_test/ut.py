# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: December 26th 2020

Modified By: hsky77
Last Updated: December 26th 2020 21:43:57 pm
'''

import enum
import asyncio
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import Column, String, Integer, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from hyssop.unit_test import UnitTestCase

from component import get_declarative_base, SQLAlchemyEntityMixin, AsyncEntityUW, AioSqliteDatabase

from . import __path__

SW_MODULES = get_declarative_base('sw_modules')


class AccountType(enum.IntEnum):
    SW_Account = 0


class AccountEntity(SW_MODULES, SQLAlchemyEntityMixin):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    account = Column(String(40), nullable=False, unique=True, index=True)
    password = Column(Text, nullable=False)
    account_type = Column(
        Enum(AccountType), default=AccountType.SW_Account, index=True)
    valid_from = Column(DateTime, default=datetime.min)
    expires_at = Column(DateTime, default=datetime.max)

    # info = relationship('AccountInfoEntity', uselist=False, cascade="all, delete",
    #                     back_populates="account")

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Generate dict that is serializable by Json convertor
        """
        return {
            'id': self.id,
            'account': self.account,
            'account_type': self.account_type,
            'valid_from': str(self.valid_from),
            'expires_at': str(self.expires_at)
        }


class AccountInfoEntity(SW_MODULES, SQLAlchemyEntityMixin):
    __tablename__ = 'account_info'

    id = Column(Integer, primary_key=True)
    email = Column(String(512))

    # account_id = Column(Integer, ForeignKey('account.id', ondelete="CASCADE"))
    # account = relationship('AccountEntity', back_populates="info")

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Generate dict that is serializable by Json convertor
        """
        return {
            'id': self.id,
            'email': self.email,
        }


AccountUW = AsyncEntityUW(AccountEntity)
AccountInfoUW = AsyncEntityUW(AccountInfoEntity)


class AioDBTestCase(UnitTestCase):
    def test(self):
        db = AioSqliteDatabase(
            SW_MODULES, file_name=__path__[0] + "/testdb.db")

        async def testAsync(index: str):
            async with db.get_connection_proxy() as conn:
                async with conn.get_cursor_proxy() as cur:
                    accounts = await AccountUW.select(cur)

                    account_data = {
                        'account': index,
                        'password': '1234',
                    }

                    account = await AccountUW.add(cur, **account_data)

                    accounts = await AccountUW.select(cur, **account_data)
                    self.assertEqual(len(accounts), 1)

                    account = await AccountUW.load(cur, **account_data)
                    self.assertIsNotNone(account)

                    account = await AccountUW.load(cur, id=account.id)
                    self.assertIsNotNone(account)

                    account = await AccountUW.merge(cur, **account.key_values)

                    await AccountUW.update(cur, account, password='5678')
                    self.assertEqual(account.password, '5678')

                    # account_info = await AccountInfoUW.add(cur, email="xxx@ooo.com", account_id=account.id)

                    await AccountUW.delete(cur, [account])

                    account = await AccountUW.load(cur, **account_data)
                    self.assertIsNone(account)

                    # await cur.commit()

        futures = []
        count = 500
        for i in range(count):
            futures.append(asyncio.ensure_future(testAsync(str(i))))

        loop = asyncio.get_event_loop()

        loop.run_until_complete(asyncio.wait(futures))

        for future in futures:
            e = future.exception()
            if e:
                print(e)

        asyncio.get_event_loop().run_until_complete(db.dispose())
