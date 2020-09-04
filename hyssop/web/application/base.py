# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 27th 2020

Modified By: hsky77
Last Updated: August 27th 2020 16:00:06 pm
'''

import logging
from typing import Any, Callable, Union, Dict
from tornado.web import Application

from ..component import DefaultComponentTypes, create_server_component_manager
from ..component.default import LocalizationComponent, LoggerComponent, CallbackComponent, ExecutorComponent, ServicesComponent
from .. import LocalCode_Application_Closing, LocalCode_Application_Closed, Component_Module_Folder


class ComponentApplicationMixin():
    def init_application_mixin(self, settings: Dict[str, Any]) -> None:
        import threading
        self.do_close = False
        self.exiting = False

        if threading.current_thread() is threading.main_thread():
            import signal
            signal.signal(signal.SIGINT, self.signal_handler)

        if Component_Module_Folder in settings:
            self.component_manager = create_server_component_manager(
                settings[Component_Module_Folder],
                settings['root_dir'])
        else:
            # default component manager
            self.component_manager = create_server_component_manager(
                None, settings['root_dir'])

        self.component_manager.invoke(
            DefaultComponentTypes.Logger, 'update_default_logger', settings['debug'])

    def signal_handler(self, signum, frame):
        self.exit()

    def exit(self):
        self.logger.info(self.comp_local.get_message(
            LocalCode_Application_Closing))
        self.do_close = True

    async def do_exit(self):
        if self.do_close:
            if not self.exiting:
                self.exiting = True
                # await
                from tornado.ioloop import IOLoop
                IOLoop.current().stop()
                await self.component_manager.dispose_components()
                self.logger.info(self.comp_local.get_message(
                    LocalCode_Application_Closed))

    @property
    def comp_local(self) -> LocalizationComponent:
        """Get the LocalizationComponent singleton instance."""
        if not hasattr(self, '_comp_local'):
            self._comp_local = self.component_manager.get_component(
                DefaultComponentTypes.Localization)
        return self._comp_local

    @property
    def comp_logger(self) -> LoggerComponent:
        """Get the LoggerComponent singleton instance."""
        if not hasattr(self, '_comp_logger'):
            self._comp_logger = self.component_manager.get_component(
                DefaultComponentTypes.Logger)
        return self._comp_logger

    @property
    def comp_callbacks(self) -> CallbackComponent:
        """Get the CallbackComponent singleton instance."""
        if not hasattr(self, '_comp_callbacks'):
            self._comp_callbacks = self.component_manager.get_component(
                DefaultComponentTypes.Callback)
        return self._comp_callbacks

    @property
    def comp_executor(self) -> ExecutorComponent:
        """Get the ExecutorComponent singleton instance."""
        if not hasattr(self, '_comp_executor'):
            self._comp_executor = self.component_manager.get_component(
                DefaultComponentTypes.Executor)
        return self._comp_executor

    @property
    def comp_services(self) -> ServicesComponent:
        """Get the ServicesComponent singleton instance."""
        if not hasattr(self, '_comp_services'):
            self._comp_services = self.component_manager.get_component(
                DefaultComponentTypes.Service)
        return self._comp_services
