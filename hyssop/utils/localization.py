import os
from typing import Dict, List, Any

from .constants import (
    LocalCode_Duplicated_Code,
    LocalCode_Local_Pack_Parsing_Error,
    LocalCode_Message_Format_Invalid,
    LocalCode_No_Code,
)
from .func import join_path


class Localization:
    """convert message to localized language message"""

    default_code = LocalCode_No_Code

    def __init__(self, lang: str = "en"):
        self.__mapping: Dict[int, Dict[str, str]] = {}  # {"code": {"lang": "string"}}
        self.__csvs = []
        self.set_language(lang)
        self.__languages = set()

    def set_language(self, lang: str) -> None:
        self.__lang = lang

    @property
    def current_language(self) -> str:
        return self.__lang

    def get_info(self) -> Dict[str, Any]:
        """return dict shows how many language avaliable and the codes loaded"""
        return {
            "current_language": self.current_language,
            "loaded_languages": list(self.__languages),
            "codes": len(self.__mapping),
            "files_loaded": self.__csvs,
        }

    def import_csvs_from_directory(self, dir: str, encoding: str = "utf-8") -> None:
        """import coded message from all csv files of indicated directory"""
        self.import_csv(
            [join_path(dir, f) for f in os.listdir(dir) if ".csv" in f and os.path.isfile(join_path(dir, f))]
        )

    def import_csv(self, files: List[str], encoding: str = "utf-8", replace_duplicated_code: bool = True) -> None:
        """import coded message from csv file"""
        import re

        for path in files:
            with open(path, "r", encoding=encoding) as f:
                self.__csvs.append(path)
                lines = f.readlines()

                langs = []
                if len(lines) > 0:
                    langs = [x.replace("\n", "") for x in lines.pop(0).split(",") if "code" not in x]

                for line in lines:
                    line = [x for x in re.split(',"(.*?)"|,', line) if x is not None and not x == "" and not x == "\n"]
                    if not len(line) - 1 == len(langs):
                        raise SyntaxError(self.get_message(LocalCode_Local_Pack_Parsing_Error, path))
                    idx = 1
                    for lang in langs:
                        self.__languages.add(lang)
                        if line[0] not in self.__mapping:
                            self.__mapping[int(line[0])] = {}

                        if lang not in self.__mapping[int(line[0])]:
                            self.__mapping[int(line[0])][lang] = line[idx].replace("\n", "")
                        else:
                            if replace_duplicated_code:
                                self.__mapping[int(line[0])][lang] = line[idx].replace("\n", "")
                            else:
                                raise KeyError(self.get_message(LocalCode_Duplicated_Code, line[0], lang))

                        idx = idx + 1

    def has_message(self, code: int) -> bool:
        return code in self.__mapping

    def get_message(self, code: int, *strings) -> str:
        """convert to localized message via code and following parameters"""
        if self.__lang not in self.__languages:
            raise KeyError("language: {}, code: {} does not exist".format(self.__lang, code))

        if code in self.__mapping:
            lang = self.__lang
            if self.__lang not in self.__mapping[code]:
                lang = "en"

            try:
                return self.__mapping[code][lang].format(*strings)
            except IndexError:
                return self.__mapping[LocalCode_Message_Format_Invalid][lang].format(code, strings)
        else:
            lang = self.__lang
            if self.__lang not in self.__mapping[self.default_code]:
                lang = "en"

            return self.__mapping[self.default_code][lang].format(self.__lang, code)
