Getting Start
******************

.. contents:: Table of Contents

Hello, World
=================

1. In command prompt, create a project named 'hello' by typing ``python3 -m hyssop create hello``
2. Start the project by typing ``python3 -m hyssop start hello``
3. Open browser to view the hello api response, http://localhost:8888/hello
4. To stop server, press **ctrl+c** in the command prompt

Hierarchy of Project
=============================

.. parsed-literal::
    project/
        component/                  # reserved folder contains the components.
            __init__.py
            ...
        controller/                 # reserved folder contains the REST api controllers
            __init__.py
            ...
        unit_test/                  # reserved folder contains the unittest test cases
            __init__.py
            ...
        pack.yaml                   # defines the files to be packed to a compressed file
        requirements.txt            # defines the required pip modules
        server_config.yaml          # server configuration

Commands
======================

.. parsed-literal::

    >python3 -m hyssop -h
    usage: hyssop [-h] {start,pack,test,create,version} ...

    optional arguments:
      -h, --help            show this help message and exit

    command:
      {start,pack,test,create,version}
        start               start server with specfied server project directory
                            path
        pack                pack server with specfied server project directory
                            path
        test                test hyssop library or specfied server project
                            directory path
        create              create a server template with specfied server project
                            directory path
        version             current hyssop version

Use Component in Controller
====================================

The hello project had defined ``HelloComponent``, and here is a example shows how to access it in controller:

.. code-block:: python

    from hyssop.web.controller.tornado import RequestController
    from component import HelloComponentTypes

    class HelloController(RequestController):
        async def get(self):
            hello_comp = self.component_manager.get_component(HelloComponentTypes.Hello)
            self.write(hello_comp.hello())

It also works with ``tornado.web.RequestHandler`` since ``component_manager`` is an attribute of ``self.application``:

.. code-block:: python

    from tornado.web import RequestHandler
    from component import HelloComponentTypes

    class HelloTornadoHandler(RequestHandler):
        async def get(self):
            hello_comp = self.application.component_manager.get_component(HelloComponentTypes.Hello)
            self.write(hello_comp.hello())

**hyssop** is currently based on `Tornado Web Server <https://www.tornadoweb.org/en/stable/>`__, 
so please visit the web-site for advanced web framework topics. 