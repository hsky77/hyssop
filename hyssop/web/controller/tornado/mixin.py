# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 20th 2020

Modified By: hsky77
Last Updated: September 20th 2020 18:47:39 pm
'''

from typing import Dict, Any

from ...component import DefaultComponentTypes, ComponentManager
from ...component.default import CallbackComponent, LocalizationComponent, ServicesComponent, ExecutorComponent, LoggerComponent, BaseSyncLogger

from ...application.tornado import TornadoApplication


class TornadoMixin():
    """hyssop controller helper functions and variables"""

    @property
    def hyssop_application(self) -> TornadoApplication:
        return self.application

    @property
    def application_name(self) -> str:
        return self.hyssop_application.settings.get('name', 'Hyssop Server')

    @property
    def component_manager(self) -> ComponentManager:
        return self.hyssop_application.component_manager

    @property
    def root_dir(self) -> str:
        return self.hyssop_application.settings['root_dir']

    @property
    def debug(self) -> bool:
        return self.hyssop_application.settings['debug'] if 'debug' in self.hyssop_application.settings else False

    @property
    def type_name(self) -> str:
        return type(self).__name__

    @property
    def component_services(self) -> ServicesComponent:
        return self.hyssop_application.comp_services

    @property
    def component_callbacks(self) -> CallbackComponent:
        return self.hyssop_application.comp_callbacks

    @property
    def component_localization(self) -> LocalizationComponent:
        return self.hyssop_application.comp_local

    @property
    def component_executor(self) -> ExecutorComponent:
        return self.hyssop_application.comp_executor

    @property
    def logger(self) -> BaseSyncLogger:
        if not hasattr(self, '_logger'):
            self._logger = self.hyssop_application.comp_logger.get_logger(
                self.type_name)
        return self._logger

    def log_info(self, msg: str, *args, exc_info=None, extra=None, stack_info=False) -> None:
        self.hyssop_application.comp_executor.run_method_in_queue(
            self.logger.info, msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info)

    def log_warning(self, msg: str, *args, exc_info=None, extra=None, stack_info=False) -> None:
        self.hyssop_application.comp_executor.run_method_in_queue(
            self.logger.warning, msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info)

    def log_error(self, msg: str, *args, exc_info=None, extra=None, stack_info=False) -> None:
        self.hyssop_application.comp_executor.run_method_in_queue(
            self.logger.error, msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info)

    def get_arguments_dict(self, include_arguments=None) -> Dict[str, Any]:
        '''Return dict of arguments with key name in include_arguments or all of the arguments when include_arguments is None'''
        if include_arguments is not None:
            return {k: self.get_argument(k, default=None)
                    for k in self.request.arguments
                    if k in include_arguments}
        else:
            return {k: self.get_argument(k, default=None)
                    for k in self.request.arguments}
