hyssop-aiohttp
******************

.. contents:: Table of Contents


**hyssop-aiohttp** is the hyssop extension that bases `aiohttp <https://docs.aiohttp.org/en/stable/>`__ and related packages to implement http interfaces of components.

**prerequests**: python 3.6+, pip

**dependencies**: `aiohttp <https://docs.aiohttp.org/en/stable/>`__, `aiohttp-swagger <https://aiohttp-swagger.readthedocs.io/en/latest/>`__, `aiohttp-cors <https://github.com/aio-libs/aiohttp-cors>`__

**Install** hyssop_aiohttp with pip: ``pip install hyssop_aiohttp``

Extended Functionalities
=============================

* Add async functions ``on_before_server_start`` to Component classes which runs after ``Component.init()`` and before aiohttp server start.

* Add "start" command to run api server by typing ``python3 -m hyssop_aiohttp start <path of your project directory>``

* Add reserved directory named "controller" as the package of aiohttp api handlers into hyssop project.

    .. parsed-literal::

        project/
            controller/                  # aiohttp api handlers.
                __init__.py
                ...

* Changes of configurations with aiohttp related packages:

    .. parsed-literal::

        name: hyssop Server
        port: 8888
        debug: False
        doc:
          api_route: <sub route of aiohttp-swagger>
          description: api document description
          version: api document version
          title: api document title
          contact: contact information

        cors:
          - origin: localhost
            allow_credentials: True
            expose_headers: '*'
            allow_headers: '*'

        controller:
          /sub_route:
            enum: <key of ControllerType to load AioHttpViews>
        aiohttp:
          route_decorators: 
            - <keys of ControllerType to load aiohttp routes decorated api handlers>

    * **port**: Port of aiohttp api server
    * **debug**: Aiohttp api server debug mode
    * **doc**: Settings of `aiohttp-swagger <https://aiohttp-swagger.readthedocs.io/en/latest/>`__
    * **cors**: Settings of `aiohttp-cors <https://github.com/aio-libs/aiohttp-cors>`__
    * **controller**: Api Sub_routes
    * **aiohttp**: Settings of aiohttp
        * **route_decorators**: Keys of ControllerType to load handlers into aiohttp routes


Usage
=============================

* **Create hyssop-aiohttp project**:

    * Create project named hello by typing ``python3 -m hyssop_aiohttp create hello``, the project hierarchy looks like the following block:
    
    .. parsed-literal::

        project/
            controller/                 # reserved folder contains aiohttp api handlers.
                __init__.py
                ...
            component/                  # reserved folder contains the components.
                __init__.py
                ...
            unit_test/                  # reserved folder contains the unittest test cases
                __init__.py
                ...
            pack.yaml                   # defines the files to be packed to a compressed file
            requirements.txt            # defines the required pip modules
            project_config.yml          # server configuration                

* **Implement controllers**:

    * Add HelloControllerTypes inherits from ControllerType into the file ``controller/__init__.py``.

    .. code-block:: python

        from hyssop.project.web import ControllerType

        class HelloControllerTypes(ControllerType):
            HelloController = ('hello_world', 'hello', 'hello')
            HelloViewController = ('hello_view', 'hello', 'HelloView')

    * Implement the handlers classes or functions.

    .. code-block:: python

        from aiohttp import web

        from hyssop_aiohttp import routes, AioHttpView

        from component import HelloComponentTypes

        class HelloView(AioHttpView):
            async def get(self):
                """
                ---
                tags:
                - hello view
                summary: hello world view get
                description: simple test controller
                produces:
                - text/html
                responses:
                    200:
                description: return hello view message
                """
                comp = self.request.app.component_manager.get_component(HelloComponentTypes.Hello)
                return web.Response(text=comp.hello())

        @routes.get('/hello')
        async def hello(request):
            """
            ---
            tags:
            - hello
            summary: hello world get
            description: simple test controller
            produces:
            - text/html
            responses:
                200:
                    description: return hello message
            """
            comp = request.app.component_manager.get_component(HelloComponentTypes.Hello)    
            return web.Response(text=comp.hello())

* Configurations:

    .. parsed-literal::

        # project_config.yml

        controller:
          /hello_view:          # handle incoming requests from /hello_view by key 'hello_view'
            enum: hello_view
        aiohttp:
          route_decorators: 
            - 'hello_world'     # load aiohttp routes decorated functions to server

* Test the handlers:

    * Run the api server by typing ``python3 -m hyssop_aiohttp start hello`` in command prompt.
    * Click `http://localhost:8888/hello <http://localhost:8888/hell>`__, `http://localhost:8888/hello_view <http://localhost:8888/hello_view>`__
