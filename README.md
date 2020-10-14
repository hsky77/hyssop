# hyssop

[![Documentation Status](https://readthedocs.org/projects/hyssop/badge/?version=latest)](https://hyssop.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://img.shields.io/pypi/v/hyssop.svg)](https://pypi.org/project/hyssop/)

**hyssop** is a pure python project adds component-based architecture and project hierarchy to opensource web frameworks. It's currently based on [Tornado Web Server](https://www.tornadoweb.org/en/stable/)

**prerequest**: python 3.6+, pip

**Install** hyssop with pip: ``pip install hyssop``

## Hello world

Create a minimal runable server project:
   * In command prompt, create a project named hello: `python3 -m hyssop create hello`
   * Start the project: `python3 -m hyssop start hello`
   * Open Browser views the response of hello api, [http://localhost:8888/hello](http://localhost:8888/hello)
   * To stop server, press **ctrl+c** in the command prompt

Read [documentation](https://hyssop.readthedocs.io/en/latest/) for more information

## Change log

* **1.0.2 - Oct. 14, 2020**:
   * Fix bugs.

* **1.0.0 - Aug. 20, 2020**:
   * Initalize project.
