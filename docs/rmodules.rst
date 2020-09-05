Modules Framework
*****************************

.. contents:: Table of Contents

How it works
=============================

**hyssop** project reserves the directories named **component**, **controller**, and **unit_test** as the packages of Components, REST APIs, and Unit Test cases. 
It's similar to how python import packages, **hyssop** loads packages with directory contains ``__init__.py`` that has the specific Enum class.
The Enum classes are the class or function importers which help **hyssop** to load the classes dynamically.

For example, the ``HelloComponent`` of hello project created in `Getting Start <getstart.html>`__,
the directory hierarchy looks like:

.. parsed-literal::
    hello/
        component/              
            __init__.py
            hello.py
        server_config.yaml


In ``__init__.py``, it defines the subclass of ``ComponentTypes``. ``ComponentTypes`` is a customized subclass of `Eunm <https://docs.python.org/3/library/enum.html>`__ class. 
Its value is a ``list`` or ``tuple`` stores ``key, package, class_or_function`` for **hyssop** maps 
the component configurations in ``server_config.yaml`` with the component classes should be imported. 

.. code-block:: python

    # __init__.py

    from hyssop.web.component import ComponentTypes

    class HelloComponentTypes(ComponentTypes):
        Hello = ('hello', 'hello', 'HelloComponent')


In ``hello.py``, it defines the ``HelloComponent`` inherits from ``Component`` class.

.. code-block:: python

    # hello.py

    from hyssop.web.component import Component

    class HelloComponent(Component):
        def init(self, component_manager, p1, *arugs, **kwargs) -> None:
            print('init Hello component load from', __package__, 'and the parameters p1:', p1)

        def hello(self):
            return 'Hello World, This is hyssop generate hello component'

In ``server_config.yaml``, add the key **'hello'** under component block. 
That tells **hyssop** load ``HelloComponent`` as **Project Component** when starting server:

.. code-block:: yaml

    # server_config.yaml:

    name: hyssop Server
    port: 8888
    debug: False
    component:
        hello: 
            p1: 'This is p1'

Make Project's Modules Work
=======================================================

Briefly list the things should be done for each reserved module:

* `controller <buildin.html#controllers>`__

    * Define the enums inherits from ``hyssop.web.controller.ControllerType`` in ``__init__.py``
    * Implement the controller class inherits from such as `hyssop.web.controller.tornado.RequestController <web_refer.html#hyssop.web.controller.RequestController>`__
    * Configre the controller block in ``server_config.yaml``

* `component <buildin.html#components>`__

    * Define the enums inherits from ``hyssop.web.component.ComponentTypes`` in ``__init__.py``
    * Implement the component class inherits from `hyssop.web.component.Component <web_refer.html#hyssop.web.component.Component>`__
    * Configre the component block in ``server_config.yaml``

* `unit_test <buildin.html#unittest-cases>`__

    * Define the enums inherits from ``hyssop.unit_test.UnitTestTypes`` in ``__init__.py``
    * Implement the test cases inherits from ``hyssop.unit_test.UnitTestCase``

Configuration Validator
=======================================================

**hyssop** provides `configurations validator <web_refer.html#configuration-validator>`__ checks the configurations of Default Components. 
Validator is extendable to validate **Project Components** and Controllers, and
the following example shows how to add validator of HelloComponent in the hello project.

.. code-block:: python

    # __init__.py

    from hyssop.web.component import ComponentTypes

    class HelloComponentTypes(ComponentTypes):
        Hello = ('hello', 'hello', 'HelloComponent')

    # add hello validator to component config validator
    from hyssop.web.config_validator import (
        ConfigContainerMeta, ConfigElementMeta, WebConfigComponentValidator)

    WebConfigComponentValidator.set_cls_parameters(
        ConfigContainerMeta('hello', False,
            ConfigElementMeta('p1', str, True) # validate 'p1' argument is required and string type
        )
    )
