Usage and Build-in Classes
****************************************

.. contents:: Table of Contents

Server Configuration
=========================

.. code-block:: yaml

    # in server_config.yaml

    name: hyssop server                 # server name
    port: 8888                          # port number
    debug: False                        # True/False enable debug mode
    ssl:
        crt: xxx.crt                    # absolute path of ssl certificate
        key: xxx.key                    # absolute path of private key file
        ca: xxx.ca                      # optional - absolute path of ca file

    controller:
        /api_route:                     # api routing path
            enum: controller_key        # key of ControllerType
            params:                     # input arguments of initialize()
                ...
        ...

    component:
        component_key:                  # key of ComponentType
            ...                         # configuration vary
        ...

* **ssl**: Enable `ssl <https://docs.python.org/3/library/ssl.html>`__ module to handle https requests.

Controllers
=========================

Controllers are the implementation of `RESTful APIs <https://restfulapi.net/>`__ to handle incomming requests.

Build-in Controllers
----------------------------------------

.. class:: enum hyssop.web.controller.DefaultControllerType.Frontend:

    Enable a general web http server, this controller directly import 
    `tornado.web.StaticFileHandler <https://www.tornadoweb.org/en/stable/web.html#tornado.web.StaticFileHandler>`__

    **enum**: ``Frontend = ('frontend', 'tornado.web', 'StaticFileHandler')``

    **config**:

    .. code-block:: yaml

        controller:
            /(.*):                                      # handle all routes
                enum: frontend
                params:
                    path: frontend                      # relative dir path under project dir
                    default_filename: index.html        # default index file

Components
=========================

Components of **hyssop** are `Singleton <https://en.wikipedia.org/wiki/Singleton>`__ functional utilities integrate Python modules or implement customized modules.
**hyssop** implements a simple `composite pattern <https://en.wikipedia.org/wiki/Composite_pattern>`__ to store and manage loaded component instances.

.. Attention:: **Default Components** are always loaded when server start. **Project Components** are loaded with keys are specified in server_config.yaml when server start.

Build-in Default Components
----------------------------------------


.. class:: enum hyssop.web.component.DefaultComponentTypes.Localization:

    Provide language localization, parameter ``dir`` is the path of directory that store the language ``.csv`` files under project directory.

    **enum**: ``Localization = ('localization', 'default', 'LocalizationComponent')``

    **config**:

    .. code-block:: yaml

        component:
            localization:
                dir: 'local'    # optional: Load the .csv files in the directory under project directory.
                lang: 'en'      # optional: Setup language, default: en.

    .. parsed-literal::
        # local/lang.csv file might looks like:
        code,en
        10000,"this is code 10000"

    **usage**:

    .. code-block:: python

        # controller class might looks like
        from hyssop.web.controller.tornado import RequestController

        class MyController(RequestController):
            async def get(self):
                self.write(self.component_localization.get_message('10000'))

.. class:: enum hyssop.web.component.DefaultComponentTypes.Logger:

    Provide **hyssop** logger control center, parameter ``dir`` is the path of directory that store the log outputs under project directory

    **enum**: ``Logger = ['logger', 'default', 'LoggerComponent']``

    **config**:

    .. code-block:: yaml

        component:
            logger:
                log_to_resources: False     # optional: Enable log to resources
                log_to_console: False       # optional: Enable log to console
                dir: 'logs'                 # optional. Log to files in the folder under porject directory if specified

    **usage**: 

    .. code-block:: python

        # controller class might looks like
        from hyssop.web.controller.tornado import RequestController

        class MyController(RequestController):
            async def get(self):
                self.log_info('test_log')

                # It could also log by getting logger
                logger = self.hyssop_application.comp_logger.get_logger(self.type_name)
                logger.info('test log')

.. class:: enum hyssop.web.component.DefaultComponentTypes.Callback:

    Callback management with ``enum.Enum class``.

    **enum**: ``Callback = ('callback', 'default', 'CallbackComponent')``

    **config**: None

    **usage**: 

    .. code-block:: python

        # This an example RequestController announces message to connected WebSocket clients
        from enum import Enum
        from hyssop.web.controller.tornado import WebSocketController, RequestController

        class MySocketCallback(Enum):
            Callback1 = 0

        class MySocketController(WebSocketController):
            def open(self):
                self.component_callbacks.add_callback(MySocketCallback.Callback1, self.__on_callback1)

            def on_close(self):
                self.component_callbacks.remove_callback(MySocketCallback.Callback1, self.__on_callback1)

            def __on_callback1(self, message: str):
                self.write_message(message)

        class MyRequestController(RequestController):
            async def post(self):
                # Execute all '__on_callback1' methods of MySocketController instances
                await self.component_callbacks.execute_callback_async(MySocketCallback.Callback1, 'test')

.. class:: enum hyssop.web.component.DefaultComponentTypes.Executor:

    Provide a simple way to execute functions synchronously and asynchronously.

    **enum**: ``Executor = ('executor', 'default', 'ExecutorComponent')``

    **config**:

    .. code-block:: yaml

        component:
            executor:
                worker_count: 1      # The maximum of workers is 2

    **usage**:

    .. code-block:: python

        # Run synchronous method __my_method in worker (different thread) asynchronously
        from hyssop.web.controller.tornado import RequestController

        class MyController(RequestController):
            async def get(self):
                async with self.component_executor.get_executor() as executor:
                    await executor.run_method_async(self.__my_method, 'arg1', 'arg2')

            def __my_method(self, arg1: str, arg2: str):
                # do something ...
                pass

.. class:: enum hyssop.web.component.DefaultComponentTypes.Service:

    Invokes web api, specified method name to enable rest mehtods

    **Enum**: ``Service = ('services', 'default', 'ServicesComponent')``

    **config**:

    .. code-block:: yaml

        component:
            services:
                async_connection_limit:             <int>   # the connections limitation in async mode
                async_connection_limit_pre_host:    <int>   # the connections limitation of each host in async mode
                routes:
                    https://www.google.com:                 # url
                        /:                                  # api_route
                            name: google                    # name of this service

    **usage**:

    .. code-block:: python

        # Invoke 'https://www.google.com/' Get
        from hyssop.web.controller.tornado import RequestController

        class MyController(RequestController):
            async def get(self):
                # by service name in server_config.yaml
                response = await self.component_services.invoke_async('google')
                self.write(response.text)

                # by url
                response = await self.component_services.invoke_async('https://www.google.com/')
                self.write(response.text)

Unittest Cases
==========================

**hyssop** reserves module **unit_test** base on `unittest <https://docs.python.org/3/library/unittest.html>`__ to test the server project or **hyssop** itself.
Define enum inherits `hyssop.unit_test.UnitTestTypes <web_refer.html#hyssop.unit_test.UnitTestCase>`__ to allow **hyssop** tests projects

* Run test in command prompt:

    * Test hyssop package by typing ``python3 -m hyssop test`` 
    * Test hyssop project by typing ``python3 -m hyssop test <project directory path>`` 

Packing Project
==========================

Packing project by typing ``python3 -m hyssop pack <project directory path>`` in command prompt.

The optional flags of command ``pack``:

    * Adding ``-w`` downloads and pack the wheel ``.whl`` lists in ``requirements.txt``. 
    * In default, ``.py`` files are compiled to ``.pyc``. Adding ``-d`` to disable the compilation.

In **hyssop** project, ``pack.yaml`` indicated the files should be packed. The block of ``include`` lists the external **files** or **directories**, 
and the block of ``exclude`` lists the **files**, **directories**, or **extensions** should be ignored. 

**usage**:

.. code-block:: yaml

    # inside pack.yaml...

    include:
    - some_file.txt         # pack some_file.txt
    - some_dir/             # pack directory 'some_dir' recursively

    exclude:
    - '.log'                # excludes files with extension '.log'
    - some_dir2/            # excludes files and sub directories under some_dir2 recursively
    - some_file2.txt        # excludes some_file2.txt