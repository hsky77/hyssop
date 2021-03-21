# hyssop

[![Documentation Status](https://readthedocs.org/projects/hyssop/badge/?version=latest)](https://hyssop.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://img.shields.io/pypi/v/hyssop.svg)](https://pypi.org/project/hyssop/)

**hyssop** is a pure python project implements component-based architecture and project hierarchy.

**prerequest**: python 3.6+, pip

**Install** hyssop with pip: ``pip install hyssop``

# Change log 

## hyssop

* **1.1.2 - Mar. 21, 2021**:
  * Add parameter "replace_duplicated_code" to Localization import_csv() in util.

* **1.1.1 - Mar. 06, 2021**:
  * Fix bugs.

* **1.1.0 - Jan. 10, 2021**:
  * Refactor the project and remove the web framework tornado dependencies. 

* **1.0.2 - Oct. 14, 2020**:
   * Fix bugs.

* **1.0.0 - Aug. 20, 2020**:
   * Initalize project.

## hyssop-aiohttp

* **0.0.3 - Mar. 06, 2021**:
  * Fix bug of aio client streaming callback.

* **0.0.2 - Feb. 15, 2021**:
  * Fix get_argument() of AioHttpRequest with given default value still raise Exception.

* **0.0.1 - Jan. 10, 2021**:
  * Integrate with [aiohttp](https://docs.aiohttp.org/en/stable/) web framework.

## hyssop-aiodb

* **0.0.4 - Mar. 06, 2021**:
  * Fix bug of value convertion in util

* **0.0.3 - Feb. 15, 2021**:
  * Fix UW class update bug with bool values.

* **0.0.2 - Feb. 02, 2021**:
  * Add mysql connection proxy pool
  * Fix aiodb mysql cursor retrived inserted row bug

* **0.0.1 - Jan. 10, 2021**:
  * Re-implement database module with [aiomysql](https://aiomysql.readthedocs.io/en/latest/index.html) & [aiosqlite](https://aiosqlite.omnilib.dev/en/stable/index.html).