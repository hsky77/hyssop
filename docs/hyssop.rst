hyssop
******************

.. contents:: Table of Contents


**hyssop** is a python project that defines project hierarchy and creates scalable component architecture which is configurable in yaml format.

**prerequest**: python 3.6+, pip

**Install** hyssop with pip: ``pip install hyssop``


Hierarchy of Project
=============================

.. parsed-literal::
    project/
        component/                  # reserved folder contains the components.
            __init__.py
            ...
        unit_test/                  # reserved folder contains the unittest test cases
            __init__.py
            ...
        pack.yaml                   # defines the files to be packed to a compressed file
        requirements.txt            # defines the required pip modules
        project_config.yml          # server configuration

Commands
======================

.. parsed-literal::

    >python3 -m hyssop -h
    usage: hyssop [-h] {start,pack,test,create,version} ...

    optional arguments:
      -h, --help            show this help message and exit

    command:
      {start,pack,test,create,version}
        test                test hyssop library or specfied project directory path
        create              create a project template with specfied project directory path
        pack                pack project with specfied project directory path
        version             print version number to console


How to create components?
=============================

The **hyssop** projects reserve the directories named **component**, and **unit_test** as the packages of Component classes, and Unit Test cases. 
It's similar to how python defines and imports packages which contain the files of ``__init__.py``.

To get start, create a template project named "hello" by typing command: ``python3 -m hyssop create hello``

The project directory should looks like:

.. parsed-literal::
    hello/
        component/              
            __init__.py
            hello.py
        unit_test/
            __init__.py
            ut1.py
        project_config.yml
        pack.yml

``component/__init__.py`` defines the subclasses of ``ComponentTypes`` that specfies the import pathes. 
The values are ``listes`` or ``tuples`` store ``keys in project_config.yml``, ``modules``, ``classes or functions``.

.. code-block:: python

    # component/__init__.py

    from hyssop.project.component import ComponentTypes

    class HelloComponentTypes(ComponentTypes):
        Hello = ('hello', 'hello', 'HelloComponent')


In ``component/hello.py``, it defines the ``HelloComponent`` inherits from ``Component`` class.

.. code-block:: python

    # component/hello.py

    from hyssop.project.component import Component

    class HelloComponent(Component):
        def init(self, component_manager, p1, *arugs, **kwargs) -> None:
            print('init Hello component load from', __package__, 'and the parameters p1:', p1)

        def hello(self):
            return 'Hello World, This is hyssop generate hello component'

In ``project_config.yml``, add the key **'hello'** under component block. 
That indicates ``HelloComponent`` should be loaded.

.. code-block:: yaml

    # project_config.yml:

    name: hyssop Project
    debug: False
    component:
        hello: 
            p1: 'This is p1'


How to test components?
=============================

``unit_test/__init__.py`` defines the subclasses of ``UnitTestTypes`` that specfies the import path of test cases.

.. code-block:: python

    # unit_test/__init__.py

    from hyssop.unit_test import UnitTestTypes

    class UTTypes(UnitTestTypes):
        UT1 = ('ut1', 'ut1', 'UT1TestCase')

In ``unit_test/ut1.py``, it defines the ``UT1TestCase`` inherits from ``UnitTestCase`` class.

.. code-block:: python

    # unit_test/ut1.py

    from hyssop.unit_test import UnitTestCase

    class UT1TestCase(UnitTestCase):
        def test(self):
            # implement unit test here...
            import os
            from component import HelloComponentTypes
            from hyssop.project.mixin import ProjectMixin

            project = ProjectMixin()
            project.load_project(os.path.dirname(os.path.dirname(__file__)))
            comp = project.component_manager.get_component(
                HelloComponentTypes.Hello)
            print(comp.hello())

Then, type the command ``python3 -m hyssop test hello`` to run all the test cases which define in ``unit_test/__init__.py``.

Configuration Validator
=======================================================

**hyssop** provides `configurations validator <web_refer.html#configuration-validator>`__ verifies the configurations. 
The following example shows how validator of HelloComponent could be customized.

.. code-block:: python

    # component/__init__.py

    from hyssop.web.component import ComponentTypesConfigComponentValidator
    from hyssop.project.config_validator import ConfigContainerMeta, ConfigElementMeta

    # add hello validator to component config validator
    ConfigComponentValidator.set_cls_parameters(
        ConfigContainerMeta('hello', False,
            ConfigElementMeta('p1', str, True) # validate HelloComponent's 'p1' argument is required and string type
        )
    )