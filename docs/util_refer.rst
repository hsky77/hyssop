``hyssop.util`` Reference
*****************************

.. contents:: Table of Contents

Worker
===================

.. class:: hyssop.util.worker.Worker

    property:

        * ``is_func_running -> bool``: Check if worker is running a function

    .. function:: run_method(func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None, **kwargs) -> bool

        Return True if the given function instance is going to be executed

        * **func**: function to be executed
        * **\*args**: arguments of **func**
        * **on_finish**: callback with the argument of function return after function runned
        * **on_exception**: callback with the argument of Exception after function Exception occured
        * **\**kwargs**: keyworded, variable-length argument list of **func**

.. class:: hyssop.util.worker.FunctionQueueWorker

    property:

        * ``pending_count -> int``: Return the length of queue

    .. function:: run_method(func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None, **kwargs) -> None

        Queue and execute the function when worker is free

        * **func**: function to be executed
        * **\*args**: arguments of **func**
        * **on_finish**: callback with the argument of function return after function runned
        * **on_exception**: callback with the argument of Exception after function Exception occured
        * **\**kwargs**: keyworded, variable-length argument list of **func**

.. class:: hyssop.util.worker.FunctionLoopWorker

    .. function:: run_method(func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None, **kwargs) -> None

        Start and loop the given function

        * **func**: function to be executed
        * **\*args**: arguments of **func**
        * **on_finish**: callback with the argument of function return after function runned
        * **on_exception**: callback with the argument of Exception after function Exception occured
        * **\**kwargs**: keyworded, variable-length argument list of **func**

    .. function:: stop()
        
        Stop if worker is looping function

Executor
===================

.. class:: hyssop.util.executor.Executor

    property:

        * ``workers() -> hyssop.util.worker.FunctionQueueWorker``: Return the Worker instance assigned to this Executor instance.

    .. function:: run_method_in_queue(self, func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None, **kwargs) -> None:

        Execute the given func in assigned Worker thread without blocking of the main thread.

        * **func**: function to be executed
        * **\*args**: arguments of **func**
        * **on_finish**: callback with the argument of function return after function runned
        * **on_exception**: callback with the argument of Exception after function Exception occured
        * **\**kwargs**: keyworded, variable-length argument list of **func**

    .. function:: run_method(self, func: Callable, *args, **kwargs) -> Any:

        Execute the given func in assigned Worker thread synchronously.

        * **func**: function to be executed
        * **\*args**: arguments of **func**
        * **\**kwargs**: keyworded, variable-length argument list of **func**

    .. function:: run_method_async(self, func: Callable, *args, **kwargs) -> Any:

        Execute the given func in assigned Worker thread asynchronously.    

        * **func**: function to be executed
        * **\*args**: arguments of **func**
        * **\**kwargs**: keyworded, variable-length argument list of **func**    

.. class:: hyssop.util.executor.ExecutorFactory

    property:

        * ``worker_count() -> int``: Return the number of worker instances.

        * ``workers() -> List[FunctionQueueWorker]``: Return the list of worker instances.

    .. function:: dispose() -> None:

        Call ``dispose()`` of each worker instance.

    .. function:: run_method_in_queue(self, func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None, **kwargs) -> None:

        Execute the given func in assigned Worker thread without blocking of the main thread.        

        * **func**: function to be executed
        * **\*args**: arguments of **func**
        * **on_finish**: callback with the argument of function return after function runned
        * **on_exception**: callback with the argument of Exception after function Exception occured
        * **\**kwargs**: keyworded, variable-length argument list of **func**

    .. function:: run_method(self, func: Callable, *args, **kwargs) -> Any:

        Execute the given func in assigned Worker thread synchronously.

        * **func**: function to be executed
        * **\*args**: arguments of **func**
        * **\**kwargs**: keyworded, variable-length argument list of **func**

    .. function:: run_method_async(self, func: Callable, *args, **kwargs) -> Any:

        Execute the given func in assigned Worker thread asynchronously.

        * **func**: function to be executed
        * **\*args**: arguments of **func**
        * **\**kwargs**: keyworded, variable-length argument list of **func**

    .. function:: get_executor(self, *args, **kwargs) -> Executor:

        Create and return Executor instance.

        * **\*args**: arguments of ``Executor.__init__()``
        * **\**kwargs**: keyworded, variable-length argument list of ``Executor.__init__()``

Util
===================

.. function:: get_class(module: str, *attrs) -> type

    return type or function instance of imported module

    example:

    .. code-block:: python

        cls = get_class("module", "class / static function", "class static function")


.. function:: join_to_abs_path(*paths) -> str

    Return os.path.join() absolute path in linux format which means replace '\\\\' to '/'

.. function:: join_path(*paths) -> str

    Return os.path.join() path in linux format which means replace '\\\\' to '/'

.. function:: walk_to_file_paths(file_or_directory: str) -> List[str]

    Return a list of absolutely path from the input directory path recursively or file
