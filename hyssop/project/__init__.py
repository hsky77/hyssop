from os import chdir
from os.path import dirname, isfile
from typing import Any, Dict, Optional, Type
from unittest import TestSuite

from yaml import SafeLoader, load

from hyssop.component import ComponentManagerT, DefaultComponentManager, create_component_manager
from hyssop.unit_test import get_test_suite
from hyssop.utils.func import join_path, join_to_abs_path


class HyssopProject:
    Dependency_Folder = "dependency"
    Component_Module_Folder = "component"
    Unittest_Module_Folder = "unit_test"

    Project_Config_File = "project_config.yml"
    Project_Pack_File = "pack.yml"
    Project_Requirement_File = "requirements.txt"

    def __init__(
        self, project_dir: str, config: Optional[Dict[str, Any]] = None, project_name: str = "hyssop project"
    ) -> None:
        self.project_dir = join_to_abs_path(project_dir)
        self.working_dir = dirname(self.project_dir)
        self.project_dir_name = self.project_dir.split("/")[-1]
        chdir(self.working_dir)

        if config is None:
            if isfile(self.config_file):
                with open(self.config_file, "r", encoding="utf8") as f:
                    config = load(f, Loader=SafeLoader)
        self.name = config.pop("name", "hyssop project") if config else project_name
        self.debug = config.pop("debug", False) if config else False
        self.config = config if config else {}

    @property
    def component_dir(self) -> str:
        return join_path(self.project_dir, self.Component_Module_Folder)

    @property
    def component_module(self) -> str:
        return f"{self.project_dir_name}.{self.Component_Module_Folder}"

    @property
    def unit_test_module(self) -> str:
        return f"{self.project_dir_name}.{self.Unittest_Module_Folder}"

    # @property
    # def project_controller_dir(self) -> str:
    #     return join_path(self.project_dir, self.Controller_Module_Folder)

    @property
    def unitetest_dir(self) -> str:
        return join_path(self.project_dir, self.Unittest_Module_Folder)

    @property
    def config_file(self) -> str:
        return join_path(self.project_dir, self.Project_Config_File)

    @property
    def pack_file(self) -> str:
        return join_path(self.project_dir, self.Project_Pack_File)

    @property
    def requirement_file(self) -> str:
        return join_path(self.project_dir, self.Project_Requirement_File)

    def create_component_manager(
        self,
        component_manager_t: Type[ComponentManagerT] = DefaultComponentManager,
    ) -> ComponentManagerT:
        return create_component_manager(
            self.project_dir,
            self.config.get(self.Component_Module_Folder, {}),
            extended_component_module_paths=[self.component_module],
            component_manager_t=component_manager_t,
        )

    def cretae_test_suite(self) -> TestSuite:
        return get_test_suite(self.unit_test_module)
