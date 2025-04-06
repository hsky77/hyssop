# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: August 21st 2020

    LoggerComponent:

        - managing logger via config setting such as:

        component:
            logger:
                log_to_resources: False     # optional: Enable log to resources
                log_to_console: False       # optional: Enable log to console
                # optional. Log to files in the folder under porject directory if specified
                dir: 'logs'

Modified By: hsky77
Last Updated: April 4th 2025 16:02:01 pm
"""


from logging import INFO, DEBUG, ERROR, Logger, getLogger, FileHandler, Formatter
from multiprocessing import Process, Queue
from os import makedirs, path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from hyssop.utils import join_path
from hyssop.utils.logger import LOG_FORMAT, MultiProcessingQueueHandle

from .base import Component


class LoggerComponentConfig(BaseModel):
    log_level: int = Field(INFO, description="Log level")
    log_to_queue: bool = Field(False, description="Enable log to multiprocessing queue")
    log_to_console: bool = Field(False, description="Enable log to console")
    log_to_file: bool = Field(False, description="Enable log to file")
    dir: Optional[str] = Field(None, description="Log to files in the folder under porject directory if specified")


class LoggerComponent(Component[LoggerComponentConfig]):
    """default component for managing logger by server config"""

    default_loggers = []

    def init(self):
        self.message_process: Optional[Process] = None
        self.message_queue: Optional[Queue] = None
        if self.config.log_to_queue:
            self.message_queue = Queue()
            self.message_process = Process(target=self.__log_from_queue, args=(self.message_queue,))

    def info(self) -> Dict[str, Any]:
        return {
            **super().info(),
            "message_process": self.message_process.pid if self.message_process else None,
            "message_queue": self.message_queue.qsize() if self.message_queue else None,
        }

    def get_logger(
        self, name: str, sub_dir: str = "", mode: str = "a", encoding: str = "utf-8", echo: bool = False
    ) -> Logger:
        """create and return logger object, sub_dir appends the path to configured log path"""
        logger = getLogger(name)
        logger.setLevel(self.config.log_level)
        logger.propagate = self.config.log_to_console or echo
        if self.config.log_to_file:
            self.update_file_handler(logger, sub_dir, mode, encoding)
        else:
            self.remove_file_handler(logger, sub_dir)

        if self.config.log_to_queue and self.message_queue:
            logger.addHandler(MultiProcessingQueueHandle(self.message_queue))

        return logger

    def update_default_logger(self, debug: bool = False) -> None:
        self.config.log_level = DEBUG if debug else ERROR
        for name in self.default_loggers:
            self.get_logger(name)
        self.config.log_level = DEBUG if debug else INFO

    def update_file_handler(self, logger: Logger, sub_dir: str = "", mode: str = "a", encoding: str = "utf-8"):
        """
        Remove logger's file handler or update it with the specfied 'log_dir'.
        """
        if self.project_dir and self.config.dir:
            log_dir = join_path(self.project_dir, self.config.dir, sub_dir)
            if not path.isdir(log_dir):
                makedirs(log_dir)
            log_file = join_path(log_dir, logger.name + ".log")

            exist = False
            for h in logger.handlers:
                if isinstance(h, FileHandler):
                    if h.baseFilename == path.abspath(log_file):
                        exist = True
                    else:
                        h.close()
                        logger.removeHandler(h)

            if not exist:
                handler = FileHandler(log_file, mode=mode, encoding=encoding)
                handler.setFormatter(Formatter(LOG_FORMAT))
                logger.addHandler(handler)

    def remove_file_handler(self, logger: Logger, sub_dir: str = ""):
        if self.project_dir and self.config.dir:
            log_file = join_path(self.project_dir, self.config.dir, sub_dir, logger.name + ".log")
            for h in logger.handlers:
                if isinstance(h, FileHandler) and h.baseFilename == path.abspath(log_file):
                    h.close()
                    logger.removeHandler(h)
                    break

    async def dispose(self):
        if self.message_process is not None and self.message_process.is_alive() and self.message_queue is not None:
            self.message_queue.put_nowait("quit process")
            self.message_process.join()

    def __log_from_queue(self, q: Queue):
        for message in iter(q.get, "quit process"):
            self._log_to_resources(message)

    def _log_to_resources(self, message: str):
        """This function will be called in different process by using multiprocessing queue."""
        pass
