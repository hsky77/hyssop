from .func import join_path
from .constants import Localization_File
from .localization import Localization

BaseLocal = Localization()
BaseLocal.import_csv([join_path(__path__[0], Localization_File)])
