# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: November 21st 2020 16:49:06 pm
'''

import os
import logging

from ...util import join_path, BaseSyncLogger, LOG_FORMAT


class FileLoggerMixin():
    def update_file_handler(self, logger: BaseSyncLogger, sub_dir: str = '', mode: str = 'a', encoding: str = 'utf-8', **kwargs):
        """
        Remove logger's file handler or update it with the specfied 'log_dir'.
        """
        log_dir = kwargs.get('dir', None)

        if log_dir:
            log_dir = join_path(kwargs.get('root_dir', ''), log_dir, sub_dir)
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir)

            log_file = join_path(kwargs.get('root_dir', ''),
                                 log_dir, sub_dir, logger.name)

            for h in logger.handlers:
                if type(h) is logging.FileHandler and h.baseFilename == os.path.abspath(log_file):
                    h.close()
                    logger.removeHandler(h)
                    break

            handler = logging.FileHandler(
                log_file, mode=mode, encoding=encoding)
            handler.setFormatter(logging.Formatter(LOG_FORMAT))
            logger.addHandler(handler)

    def remove_file_handler(self, logger: BaseSyncLogger, sub_dir: str = '', **kwargs):
        log_dir = kwargs.get('dir', None)

        if log_dir:
            log_dir = join_path(kwargs.get('root_dir', ''), log_dir, sub_dir)

            log_file = join_path(kwargs.get('root_dir', ''),
                                 log_dir, sub_dir, logger.name)

            for h in logger.handlers:
                if type(h) is logging.FileHandler and h.baseFilename == os.path.abspath(log_file):
                    h.close()
                    logger.removeHandler(h)
                    break
