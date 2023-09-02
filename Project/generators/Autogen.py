from pathlib import Path
# ...

from __main__ import BinderBase


class TemplateBinder(BinderBase):
    @staticmethod
    def get_template_path() -> Path:
        ...

    @staticmethod
    def get_output_path() -> Path:
        ...

    @staticmethod
    def get_template_config() -> dict:
        ...
