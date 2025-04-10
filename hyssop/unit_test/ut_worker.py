# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: August 21st 2020

Modified By: hsky77
Last Updated: April 6th 2025 05:19:22 am
"""

import asyncio
import time

from hyssop.utils.executor import ExecutorFactory
from hyssop.utils.worker import FunctionLoopWorker, FunctionQueueWorker, Worker

from .base import IUnitTestCase


class TestCaseWorker(IUnitTestCase):
    def test(self):
        # self.test_pools()
        self.test_workers()

    def test_pools(self):
        """test worker pool both sync and async function"""
        worker_count = 1
        ap = ExecutorFactory(worker_limit=worker_count)

        def foo(index, count):
            self.assertIsNotNone(index)
            return index

        def foo_raise_exception(index, kwindex):
            self.assertIsNotNone(index)
            raise Exception("This is from foo_raise_exception()")

        result = ap.run_method(foo, 1, 1)
        self.assertEqual(result, 1)

        with ap.get_executor() as executor:
            result = executor.run_method(foo, 2, 1)
            self.assertEqual(result, 2)

            try:
                executor.run_method(foo_raise_exception, 1, 3)
            except Exception as e:
                self.assertEqual(str(e), "This is from foo_raise_exception()")

        async def async_foo(index):
            result = await ap.run_method_async(foo, index, 1)
            self.assertEqual(result, index)

            try:
                await ap.run_method_async(foo_raise_exception, index, 3)
            except Exception as e:
                self.assertEqual(str(e), "This is from foo_raise_exception()")

            async with ap.get_executor() as executor:
                result = await executor.run_method_async(foo, index, 1)
                self.assertEqual(result, index)

                try:
                    await executor.run_method_async(foo_raise_exception, index, 3)
                except Exception as e:
                    self.assertEqual(str(e), "This is from foo_raise_exception()")

        futures = []
        count = 10000
        for i in range(count):
            futures.append(asyncio.ensure_future(async_foo(i)))

        asyncio.run(asyncio.wait(futures))
        ap.dispose()
        self.assertLessEqual(ap.worker_count, worker_count)

    def test_workers(self):
        """test function and callback have been executed properly, it should takes 2~3 secs"""

        self.check_exp = False
        self.loop_count = 0

        def foo(index, kwindex):
            self.assertIs(index, 1)
            self.assertIs(kwindex, 2)
            self.loop_count = self.loop_count + 1
            return index

        def foo_raise_exception(index, kwindex):
            self.assertIs(index, 1)
            self.assertIs(kwindex, 2)
            self.loop_count = self.loop_count + 1
            raise Exception("This is from foo_raise_exception()")

        def on_finish(result):
            self.assertIs(result, 1)

        def on_exception(e):
            self.assertEqual(str(e), "This is from foo_raise_exception()")
            self.check_exp = True

        with Worker() as worker:
            worker.run_method(foo, 1, kwindex=2, on_finish=on_finish, on_exception=on_exception)

            while worker.is_func_running:
                pass

            self.check_exp = False
            worker.run_method(foo_raise_exception, 1, kwindex=2, on_finish=on_finish, on_exception=on_exception)

            while worker.is_func_running:
                pass

            self.assertTrue(self.check_exp)

        with FunctionQueueWorker() as worker:
            self.check_exp = False
            worker.run_method(foo, 1, kwindex=2, on_finish=on_finish, on_exception=on_exception)

            worker.run_method(foo_raise_exception, 1, kwindex=2, on_finish=on_finish, on_exception=on_exception)

            start_time = time.time()
            while worker.pending_count > 0:
                self.assertGreaterEqual(3, time.time() - start_time)

            self.assertTrue(self.check_exp)

        with FunctionLoopWorker(loop_interval_seconds=0.1) as worker:
            self.check_exp = False
            self.loop_count = 0
            wait_time = 0.5

            worker.run_method(foo, 1, kwindex=2, on_method_runned=on_finish, on_exception=on_exception)

            start_time = time.time()
            while time.time() - start_time < wait_time:
                pass

            self.assertGreaterEqual(self.loop_count, 2)

            self.loop_count = 0
            worker.run_method(foo_raise_exception, 1, kwindex=2, on_method_runned=on_finish, on_exception=on_exception)

            start_time = time.time()
            while time.time() - start_time < wait_time:
                pass

            self.assertGreaterEqual(self.loop_count, 2)
