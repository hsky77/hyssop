import asyncio
from os import mkdir
from os.path import isdir, isfile
from typing import Any, Dict, List, Optional, Type

from aiohttp import web

from hyssop.component import add_default_component_module_path
from hyssop.component.constants import LocalCode_File_Not_Found
from hyssop.project import HyssopProject
from hyssop.utils import BaseLocal
from hyssop.utils.func import join_path

from .base import ControllerTypes

routes = web.RouteTableDef()
add_default_component_module_path("hyssop_aiohttp.component")


class AioHttpRequest(web.Request):
    @property
    def app(self) -> "AioHttpApplication":
        return super().app  # type: ignore

    @property
    def component_manager(self):
        return self.app.component_manager

    @property
    def project(self):
        return self.app.project

    def get_logger(self, name: str):
        return self.component_manager.get_logger(name)

    def get_message(self, code: int, *args: Any):
        return self.component_manager.get_message(code, *args)

    async def get_argument(self, name: str, *default) -> Any:
        """
        Get argument from query string or body data.
        Return default or raise HTTPBadRequest exception if that does not exist.
        """
        if not hasattr(self, "_parsed_body"):
            if self.content_type == "application/json":
                self._parsed_body = await self.json()
            else:
                self._parsed_body = await self.post()

        data = {**self.query, **self._parsed_body}
        if name in data:
            return data[name]
        else:
            if len(default) > 0:
                return default[0]
            else:
                raise web.HTTPBadRequest(text=str(KeyError(name)))

    async def get_arguments_dict(self, keys: Optional[List[str]] = None):
        """
        Get arguments dict from query string or body data with indicated args.
        """
        if not hasattr(self, "_parsed_body"):
            if self.content_type == "application/json":
                self._parsed_body = await self.json()
            else:
                self._parsed_body = await self.post()

        data = {**self.query, **self._parsed_body}
        if keys:
            return {k: v for k, v in data.items() if k in keys}
        else:
            return data


class AioHttpHyssopProject(HyssopProject):
    Controller_Module_Folder = "controller"

    def __init__(self, project_dir, config=None, project_name="hyssop project"):
        super().__init__(project_dir, config, project_name)
        self.port = self.config.pop("port", 8888)

    @property
    def controller_dir(self) -> str:
        return join_path(self.project_dir, self.Controller_Module_Folder)

    @property
    def controller_module(self) -> str:
        return f"{self.project_dir_name}.{self.Controller_Module_Folder}"

    @property
    def ssl_context(self):
        ssl_data: Optional[Dict[str, Any]] = self.config.get("ssl", None)
        if ssl_data is not None:
            if not isfile(join_path(ssl_data["crt"])):
                raise FileNotFoundError(BaseLocal.get_message(LocalCode_File_Not_Found, join_path(ssl_data["crt"])))
            if not isfile(join_path(ssl_data["key"])):
                raise FileNotFoundError(BaseLocal.get_message(LocalCode_File_Not_Found, join_path(ssl_data["key"])))

            import ssl

            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(join_path(ssl_data["crt"]), join_path(ssl_data["key"]))
            ca: Optional[str] = ssl_data.get("cs", None)
            if ca is not None:
                if not isfile(join_path(ca)):
                    raise FileNotFoundError(BaseLocal.get_message(LocalCode_File_Not_Found, join_path(ca)))
                ssl_ctx.load_verify_locations(join_path(ca))
            return ssl_ctx

    def create_controllers(self):
        return ControllerTypes.get_dynamic_classes_types(self.controller_module)

    def init_controllers(self):
        controller_types = self.create_controllers()
        aiohttp_data: Optional[Dict[str, Any]] = self.config.get("aiohttp", None)
        if aiohttp_data:
            static_file: Optional[Dict[str, Any]] = aiohttp_data.get("static_file", None)
            if static_file:
                for k, v in static_file.items():
                    path = self.project_dir + k
                    if not isdir(path):
                        mkdir(path)
                    # add_routes([web.static(k, path, **v)])

            www: Optional[str] = aiohttp_data.get("www", None)
            if www:
                path = f"{self.project_dir}/{www}"
                if not isdir(path):
                    mkdir(path)
                # self.add_routes([web.static("/", path)])

            route_decorators: Optional[List[str]] = aiohttp_data.get("route_decorators", None)
            if route_decorators:
                for controller_type in controller_types:
                    for name, _ in controller_type.get_dynamic_functions():
                        if name in route_decorators:
                            # self.add_routes([controller_class.get_route()])
                            pass
            # self.add_routes(routes)

        # for controller in self.project_controllers:
        #     if inspect.isclass(controller[1]) and issubclass(controller[1], web.View):
        #         self.router.add_view(controller[0], controller[1])

        # Setup aiohttp swagger
        # doc: Dict[str, str] = self.config.get("doc", None)
        # if doc:
        #     from aiohttp_swagger import setup_swagger

        #     api_route = doc.get("api_route", "/api/doc")
        #     description = doc.get("description", "Swagger API definition")
        #     api_version = doc.get("version", "1.0.0")
        #     title = doc.get("title", "Swagger API")
        #     contact = doc.get("contact", "")

        #     setup_swagger(
        #         self,
        #         swagger_url=api_route,
        #         description=description,
        #         api_version=api_version,
        #         title=title,
        #         contact=contact,
        #     )

        # Setup Cors settings
        # cors = self.config.get("cors", None)
        # if cors:
        #     from aiohttp_cors import ResourceOptions, setup

        #     cors_settings = {}
        #     for cors_setting in self.project_config["cors"]:
        #         cors_settings[cors_setting["origin"]] = ResourceOptions(
        #             **{k: v for k, v in cors_setting.items() if not k == "origin"}
        #         )
        #     cors = setup(self, defaults=cors_settings)
        #     for route in list(self.router.routes()):
        #         cors.add(route)


class AioHttpApplication(web.Application):

    @property
    def port(self) -> int:
        return self.project.port

    async def start_components(self, app: web.Application):
        await self.component_manager.start_components()

    async def dispose_components(self, app: web.Application):
        await self.component_manager.dispose_components()

    def init_server_with_project(self, project: AioHttpHyssopProject):
        from hyssop.component import DefaultComponentTypes

        self.project = project
        self.component_manager = project.create_component_manager()
        self.project.init_controllers()
        self.on_startup.append(self.start_components)
        self.on_cleanup.append(self.dispose_components)

        comp = self.component_manager.get_component(DefaultComponentTypes.Logger)
        comp.default_loggers += ["aiohttp.access", "aiohttp.web", "aiohttp.server"]
        comp.update_default_logger(project.debug)

    def _make_request(
        self,
        message,
        payload,
        protocol,
        writer,
        task: "asyncio.Task[None]",
        _cls: Type[web.Request] = AioHttpRequest,
    ):
        return super()._make_request(message, payload, protocol, writer, task, _cls)


# class AioHttpView(web.View, aiohttp_cors.mixin.CorsViewMixin):
#     @property
#     def request(self) -> AioHttpRequest:
#         return super().request

#     async def get_argument(self, name: str, default: Any = None) -> Any:
#         return await self.request.get_argument(name, default)

#     async def get_arguments_dict(self, args: List[str] = None) -> MultiDictProxy:
#         return await self.request.get_arguments_dict(args)


class AioHttpServer:
    def __init__(self, project_dir: str):
        self.app = AioHttpApplication()
        self.app.init_server_with_project(AioHttpHyssopProject(project_dir))
        self.app.add_routes(routes)

    def start(self):
        web.run_app(self.app, port=self.app.port, ssl_context=self.app.project.ssl_context)
