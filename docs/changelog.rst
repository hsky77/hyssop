Change log
=====================================

* **hyssop**

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

* **hyssop-aiohttp**

  * **0.0.7 - Sep. 18, 2021**:

    * Fix bugs of loading aiohttp route_decorators

  * **0.0.6 - Mar. 27, 2021**:

    * Fix bug: add aiohttp.server to default loggers.
    * Add [aiohttp-cors](https://github.com/aio-libs/aiohttp-cors) applys apis and views

  * **0.0.3 - Mar. 06, 2021**:

    * Fix bug of aio client streaming callback.

  * **0.0.2 - Feb. 15, 2021**:

    * Fix get_argument() of AioHttpRequest with given default value still raise Exception.

  * **0.0.1 - Jan. 10, 2021**:

    * Integrate with [aiohttp](https://docs.aiohttp.org/en/stable/) web framework.

* **hyssop-aiodb**

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
