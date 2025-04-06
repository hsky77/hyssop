# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
File created: August 21st 2020

This module provides localization functionality for Hyssop framework.

Modified By: hsky77
Last Updated: April 3rd 2025 09:20:34 am
"""

from os.path import dirname
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from hyssop.utils import BaseLocal, join_path

from .base import Component


class LocalizationComponentConfig(BaseModel):
    csv_files: List[str] = Field(default_factory=list, description="localization csv files")
    dir: Optional[str] = Field(None, description="directory of localization csv files")
    lang: str = Field("en", description="message language")


class LocalizationComponent(Component[LocalizationComponentConfig]):
    """default component for managing localized message by config setting"""

    def init(self) -> None:
        self.local = BaseLocal
        # default csv
        self.local.import_csvs_from_directory(dirname(__file__))
        self.local.import_csv(self.config.csv_files)
        if self.config.dir is not None:
            self.local.import_csvs_from_directory(join_path(self.project_dir, self.config.dir))
        self.local.set_language(self.config.lang)

    def info(self) -> Dict[str, Any]:
        return {**super().info(), **self.local.get_info()}

    @property
    def current_language(self) -> str:
        """Get current message language"""
        return self.local.current_language

    def set_language(self, lang: str) -> None:
        """Set message language"""
        self.local.set_language(lang)

    def get_message(self, code: int, *args) -> str:
        """Format to localized message."""
        return self.local.get_message(code, *args)
