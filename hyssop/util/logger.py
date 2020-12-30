# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: November 22nd 2020 14:43:18 pm
'''

import logging
from threading import Lock

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(name)s  - %(message)s'


def configure_colored_logging(loglevel: str = 'INFO', logger: logging.Logger = None) -> None:
    """
    note: only call once at the beginning of program
    """
    import coloredlogs
    field_styles = coloredlogs.DEFAULT_FIELD_STYLES.copy()
    field_styles['asctime'] = {}
    level_styles = coloredlogs.DEFAULT_LEVEL_STYLES.copy()
    level_styles['debug'] = {}
    if logger is not None:
        coloredlogs.install(
            level=loglevel,
            use_chroot=False,
            fmt=LOG_FORMAT,
            level_styles=level_styles,
            field_styles=field_styles,
            logger=logger)
    else:
        coloredlogs.install(
            level=loglevel,
            use_chroot=False,
            fmt=LOG_FORMAT,
            level_styles=level_styles,
            field_styles=field_styles)


class BaseSyncLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.INFO):
        super().__init__(name, level)
        self.lock = Lock()

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        with self.lock:
            super()._log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)


logging.setLoggerClass(BaseSyncLogger)
