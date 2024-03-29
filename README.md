# hyssop

[![Documentation Status](https://readthedocs.org/projects/hyssop/badge/?version=latest)](https://hyssop.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://img.shields.io/pypi/v/hyssop.svg)](https://pypi.org/project/hyssop/)

**hyssop** is a python project that defines project hierarchy and creates scalable component architecture which is configurable in yaml format file.

**prerequest**: python 3.6+, pip

**Install** hyssop with pip: ``pip install hyssop``

# Change logs

## hyssop

* **1.1.7 - May. 21, 2022**:
  * refactor loading and disposing components in order

* **1.1.6.1 - May. 7, 2022**:
  * Fix bug of loading components

* **1.1.6 - May. 7, 2022**:
  * Localization: using default language messages if the localized message does not exist.
  * Fix bug of component manager gets component failed when importing the same component type with different pathes that create different instances

* **1.1.5 - Oct. 7, 2021**:
  * Remove package dependency of "coloredlogs".

* **1.1.4 - Oct. 7, 2021**:
  * Fix bug - logger component: sub folder path of logger file.

* **1.1.3 - Mar. 21, 2021**:
  * Add parameter "replace_duplicated_code" to Localization import_csv() in util.
  * Fix bug: logger file path is incorrect

* **1.1.1 - Mar. 06, 2021**:
  * Fix bugs.

* **1.1.0 - Jan. 10, 2021**:
  * Refactor the project and remove the web framework tornado dependencies. 

* **1.0.2 - Oct. 14, 2020**:
   * Fix bugs.

* **1.0.0 - Aug. 20, 2020**:
   * Initalize project.

## hyssop-aiohttp

* **0.0.7 - May. 7, 2022**:
  * Fix exceptions does not raise when loading aiohttp route_decorators

* **0.0.6 - Mar. 27, 2021**:
  * Fix bug: add aiohttp.server to default loggers.
  * Add [aiohttp-cors](https://github.com/aio-libs/aiohttp-cors) applys apis and views

* **0.0.3 - Mar. 06, 2021**:
  * Fix bug of aio client streaming callback.

* **0.0.2 - Feb. 15, 2021**:
  * Fix get_argument() of AioHttpRequest with given default value still raise Exception.

* **0.0.1 - Jan. 10, 2021**:
  * Integrate with [aiohttp](https://docs.aiohttp.org/en/stable/) web framework.

## hyssop-aiodb

* **0.0.7 - Apr. 7, 2021**:
  * Fix bug of value convertion in util
  * Fix bug of AsyncEntityUW update().
  * Add timer to reconnect db connections

* **0.0.3 - Feb. 15, 2021**:
  * Fix UW class update bug with bool values.

* **0.0.2 - Feb. 02, 2021**:
  * Add mysql connection proxy pool
  * Fix aiodb mysql cursor retrived inserted row bug

* **0.0.1 - Jan. 10, 2021**:
  * Re-implement database module with [aiomysql](https://aiomysql.readthedocs.io/en/latest/index.html) & [aiosqlite](https://aiosqlite.omnilib.dev/en/stable/index.html).