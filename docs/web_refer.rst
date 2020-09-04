``hyssop.web`` Reference
*****************************

.. contents:: Table of Contents

Controllers based on Tornado
=============================

.. class:: hyssop.web.controller.TornadoMixin

    A helper class defines quick function access components

    **Property**:

    * ``hyssop_application -> TornadoApplication``: Return ``hyssop.web.application.TornadoApplication`` instance

    * ``application_name -> str``: Return application name.

    * ``component_manager -> ComponentManager``: Return `ComponentManager <web_refer.html#hyssop.web.component.ComponentManager>`__ instance

    * ``root_dir -> str``: Return the path string of project directory.

    * ``debug -> bool``: Check is in debug mode.
    
    * ``component_services -> ServicesComponent``: Return singleton `ServicesComponent <web_refer.html#hyssop.web.component.default.ServicesComponent>`__ instance.

    * ``component_callbacks -> CallbackComponent``: Return singleton `CallbackComponent <web_refer.html#hyssop.web.component.default.CallbackComponent>`__ instance.

    * ``component_localization -> LocalizationComponent``: Return singleton `LocalizationComponent <web_refer.html#hyssop.web.component.default.LocalizationComponent>`__ instance.

    * ``component_executor -> ExecutorComponent``: Return singleton `ExecutorComponent <web_refer.html#hyssop.web.component.default.ExecutorComponent>`__ instance.

    * ``logger -> BaseSyncLogger``: Return singleton logger instance.

    .. function :: log_info(self, msg: str, *args, exc_info=None, extra=None, stack_info=False) -> None:
    
        Log in info level

    .. function :: log_warning(self, msg: str, *args, exc_info=None, extra=None, stack_info=False) -> None:
    
        Log in warning level

    .. function :: log_error(self, msg: str, *args, exc_info=None, extra=None, stack_info=False) -> None:

        Log in error level

.. class:: hyssop.web.controller.RequestController

    Class inherits from `tornado.web.RequestHandler <https://www.tornadoweb.org/en/stable/web.html#request-handlers>`__.
    Please check the usage of tornado documentation

.. class:: hyssop.web.controller.StreamingDownloadController

    Abstract class inherits from `hyssop.web.controller.RequestController <web_refer.html#hyssop.web.controller.RequestController>`__.

    .. function:: _prepare_binary()-> List[Byte]

        override this awaitable function to prepare binary data for downloading

.. class:: hyssop.web.controller.StreamingUploadController

    Abstract class inherits from `hyssop.web.controller.RequestController <web_refer.html#hyssop.web.controller.RequestController>`__.

    .. function:: _on_chunk_received(self, headers, chunk, bytes_size_received):

        override this function to process incoming chunks

    .. function:: _on_data_received(self, headers, bytes_size_received):

        override this function to do process after data transaction completed

.. class:: hyssop.web.controller.StreamingFileUploadController

    Class inherits from `hyssop.web.controller.RequestController <web_refer.html#hyssop.web.controller.RequestController>`__.

.. class:: hyssop.web.controller.WebSocketController

    Class inherits from `tornado.websocket.WebSocketHandler <https://www.tornadoweb.org/en/stable/websocket.html#tornado.websocket.WebSocketHandler>`__.
    Please check the usage of tornado documentation

Components
===================

.. class:: hyssop.web.component.Component

    Base abstract class of component

    .. function:: init(component_manager, \*arugs, \*\*kwargs) -> None

        Execute when ComponentManager initialize component objects.

    .. function:: info() -> Dict
    
        Return define meta information of component

    .. function:: dispose(component_manager) -> None

        Execute when ComponentManager dispose() is called.

.. class:: hyssop.web.component.ComponentManager

    Contain and manage the loaded components

    .. function:: @property components -> List[Component]

        Return list of loaded components

    .. function:: @property info -> Dict

        Return dict of loaded components info

    .. function:: dispose() -> None

        Call dispose() of loaded components

    .. function:: boardcast(method\: str, \*arugs, \*\*kwargs) -> List[Tuple[ComponentTypes, Any]]

        Invokes the non-awaitable method of stored components and
        return a list of returns from each component method

        * **method**: method name to be executed
        * **\*args**: arguments of **method**
        * **\**kwargs**: keyworded, variable-length argument list of **method**

    .. function:: boardcast_async(method\: str, \*arugs, \*\*kwargs) -> List[Tuple[ComponentTypes, Any]]

        Invokes both awaitable and non-awaitable method of stored components and 
        return a list of returns from each component method

        * **method**: method name to be executed
        * **\*args**: arguments of **method**
        * **\**kwargs**: keyworded, variable-length argument list of **method**

    .. function:: invoke(enum_type\: ComponentTypes, method\: str, \*arugs, \**kwargs) -> Any

        Execute component mehtod by the method name and arguments

        * **enum_type**: ComponentTypes of target Component
        * **method**: method name to be executed
        * **\*args**: arguments of **method**
        * **\**kwargs**: keyworded, variable-length argument list of **method**

    .. function:: invoke_async(enum_type\: ComponentTypes, method\: str, \*arugs, \**kwargs) -> Any

        Asynchronously execute component mehtod by giving the method name and arguments

        * **enum_type**: ComponentTypes of target Component
        * **method**: method name to be executed
        * **\*args**: arguments of **method**
        * **\**kwargs**: keyworded, variable-length argument list of **method**

    .. function:: set_component(component\: Component) -> None

        Add or replace component instance

        * **component**: Component instance

    .. function:: get_component(enum_type\: ComponentTypes) -> Union[Component, None]

        Return stored component instance or None if it does not exist.

        * **enum_type**: ComponentTypes of target Component

    .. function:: has_component(enum_type\: ComponentTypes) -> bool

        Check whether component is loaded

        * **enum_type**: ComponentTypes of target Component

    .. function:: sort_components(order_list\: List[ComponentTypes]) -> None

        Sort component object with ComponentTypes in order

        * **order_list**: list of ComponentTypes

.. class:: hyssop.web.component.default.LocalizationComponent

    .. function:: set_language(lang\: str) -> None

        Set language

        * **lang**: key of language such as 'en'

    .. function:: get_message(code\: str, \*args) -> str

        Return the message refer to 'code' and \*args

        * **code**: localized message code
        * **\*args**: variable number of arguments of ``str``
                
.. class:: hyssop.web.component.default.LoggerComponent

    .. function:: update_default_logger(self, debug: bool = False) -> None:

        Enable/disable default loggers print to stdout, use ``add_module_default_logger`` to add default loggers.

        * **debug**: Set log level to be logging.DEBUG

    .. code-block:: python

        from hyssop.web.component import add_module_default_logger

        # add package logger as the default logger in logger component
        add_module_default_logger(['package_default_logger'])

    .. function:: get_logger(self, name: str, *args, sub_dir: str = '', mode: str = 'a', encoding: str = 'utf-8', echo: bool = False) -> BaseSyncLogger:

        The ``hyssop.web.component.default.LoggerComponent`` inherits ``hyssop.web.component.mixin.FileLoggerMixin`` to add ``logging.FileHandler`` to logger instances.
        Override this method to add different logging handlers to customize your own logger class, and 
        modified the value of ``hyssop.web.component.DefaultComponentTypes.Logger`` to allow hyssop load the customized LoggerComponent class.

        * **name**: logger name
        * **\*args**: arguments of **method**
        * **sub_dir**: specfied sub dir of log dir if enable logging to file
        * **mode**: filemode
        * **encoding**: text encoding
        * **echo**: print log to command prompt
        * **\**kwargs**: keyworded, variable-length argument list of **method**

    .. code-block:: python
        
        from hyssop.web.component.default import LoggerComponent

        class MyLoggerComponent(LoggerComponent):
            def get_logger(self, 
                            name: str, 
                            *args, 
                            echo: bool = False) -> BaseSyncLogger:
                logger = self.loggers[name] if name in self.loggers else None

                if not logger:
                    logger = logging.getLogger(name)

                    if self.log_to_resources:
                        # update logger handlers here...
                        pass

                self.loggers[name] = logger

                if logger:
                    logger.setLevel(self.log_level)
                    logger.propagate = self.log_echo or echo

                return logger

        from hyssop.web.component import DefaultComponentTypes
        # replace with module name and class name of MyLoggerComponent
        DefaultComponentTypes.Logger.value[1] = __package__
        DefaultComponentTypes.Logger.value[2] = 'MyLoggerComponent'

.. class:: hyssop.web.component.default.CallbackComponent

    .. function:: get_callback_obj(enum_cls\: Enum) -> Callbacks

        Return ``hyssop.util.Callbacks`` instance

        * **enum_cls**: class of ``enum``

    .. function:: add_callback(callback_enum_type\: Enum, callback\: Callable) -> None

        Registered callback function

        * **callback_enum_type**: class of ``enum``
        * **callback**: callback function

    .. function:: remove_callback(callback_enum_type\: Enum, callback\: Callable) -> None

        Remove callback function

        * **callback_enum_type**: class of ``enum``
        * **callback**: callback function

    .. function:: execute_callback(callback_enum_type\: Enum, \*args, \**kwargs) -> None

        Execute registered callback functions

        * **callback_enum_type**: class of ``enum``
        * **\*args**: arguments of callback functions
        * **\**kwargs**: keyworded, variable-length argument list of callback functions     

    .. function:: execute_callback_async(callback_enum_type\: Enum, \*args, \**kwargs) -> None

        Asynchronously execute registered callback functions

        * **callback_enum_type**: class of ``enum``
        * **\*args**: arguments of callback functions
        * **\**kwargs**: keyworded, variable-length argument list of callback functions

.. class:: hyssop.web.component.default.ExecutorComponent

    .. function:: run_method_in_queue(self, func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None, **kwargs) -> None:

        Execute ``func`` without blocking of the main thread.

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

    .. function:: get_executor(self) -> Executor:

        Create and return Executor instance.

.. class:: hyssop.web.component.default.ServicesComponent

    **Property**:

    * ``async_client(self) -> aiohttp.ClientSession``: Return aiohttp.ClientSession instance.

    .. function:: invoke(self, service_name_or_url: str, method: str = 'get', sub_route: str = '', streaming_callback: Callable = None, chunk_size: int = STREAMING_CHUNK_SIZE, **kwargs) -> requests.Response:

        Send http request to config specfied service_name or url, and return ``requests.Response`` instance.

        * **service_name_or_url**: Config specfied service_name or url.
        * **method**: Http methods ``['get', 'post', 'patch', 'put', 'delete', 'option']``
        * **sub_route**: Additional route string add to the end of request url
        * **streaming_callback**: Streaming callback function, check `Reference <https://requests.readthedocs.io/en/master/user/advanced/#streaming-uploads>`__
        * **chunk_size**: Only work with streaming callback function is not None.
        * **\**kwargs**: Keyworded, variable-length argument list of http method parameters

    .. function:: invoke_async(self, service_name_or_url: str, method: str = 'get', sub_route: str = '', streaming_callback: Callable = None, chunk_size: int = STREAMING_CHUNK_SIZE, **kwargs) -> requests.Response:

        Asynchronously send http request to config specfied service_name or url, and return ``requests.Response`` instance

        * **service_name_or_url**: Config specfied service_name or url.
        * **method**: Http methods ``['get', 'post', 'patch', 'put', 'delete', 'option']``
        * **sub_route**: Additional route string add to the end of request url
        * **streaming_callback**: Streaming callback function, check `Reference <https://requests.readthedocs.io/en/master/user/advanced/#streaming-uploads>`__
        * **chunk_size**: Only work with streaming callback function is not None.
        * **\**kwargs**: Keyworded, variable-length argument list of http method parameters

Configuration Validator 
===============================

.. class:: hyssop.web.config_validator.ConfigBaseElementMeta

    base config element metaclass

    .. function:: set_cls_parameters(*cls_parameters) -> None

        **@classmethod**, set the sub class elements

        * **\*parameters**: variable number of arguments of ConfigBaseElementMeta
    
    .. function:: get_cls_parameter(key_routes, delimeter=".") -> type

        **@classmethod**, get the sub class elements

        * **key_routes**: route in ``str``
        * **delimeter**: delimeter of route.split()

    .. function:: get_parameter(key_routes: str, delimeter: str = '.')

        return parameter of specfied key_routes

        * **key_routes**: route in ``str``
        * **delimeter**: delimeter of route.split()

.. class:: hyssop.web.config_validator.ConfigContainerMeta

    Configration validation element metaclass contain sub elements

    .. function:: __new__(name: str, required: bool, *parameters) -> type

        * **name**: name of type
        * **required**: specfied is this element is required in config
        * **\*parameters**: variable number of arguments of ConfigBaseElementMeta

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hyssop.web.config_validator.ConfigElementMeta

    Configration validation element metaclass store parameters

    .. function:: __new__(name: str, parameter_type: Any, required: bool) -> type

        * **name**: name of type
        * **parameter_type**: variable type such ``str, int, float``
        * **required**: specfied is this element is required in config

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hyssop.web.config_validator.ConfigScalableContainerMeta

    scalable configration validation element metaclass contain sub elements metaclass

    .. function:: __new__(parameter_type: Union[str, int], *parameters) -> type

        * **parameter_type**: variable type such ``str, int, float``
        * **\*parameters**: variable number of arguments of ConfigBaseElementMeta

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hyssop.web.config_validator.ConfigScalableElementMeta

    scalable configration validation element metaclass

    .. function:: __new__(element_type: Union[str, int], parameter_type: Any) -> type

        * **element_type**: scalable key variable type such as ``str, int, float``
        * **parameter_type**: variable type such as ``str, int, float``

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hyssop.web.config_validator.ConfigSwitchableElementMeta

    switchable configration validation element metaclass

    .. function:: __new__(name: str, parameter_type: Any, required: bool, *parameters) -> type

        * **name**: name of type
        * **parameter_type**: variable type
        * **required**: specfied is this element is required in config
        * **\*parameters**: variable number of arguments of ConfigBaseElementMeta

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hyssop.web.config_validator.WebConfigValidator

    default validator to validate ``server_config.yaml``.

.. class:: hyssop.web.config_validator.WebConfigControllerValidator

    default validator to validate the controller block of ``server_config.yaml``.

.. class:: hyssop.web.config_validator.WebConfigComponentValidator

    default validator to validate the component block of ``server_config.yaml``.

