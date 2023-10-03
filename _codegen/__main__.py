from abc import abstractmethod
from importlib.machinery import SourceFileLoader
import inspect
from pathlib import Path
from typing import final, runtime_checkable, Generator, Protocol

from jinja2 import FileSystemLoader, Environment


@runtime_checkable
class BinderBase(Protocol):
    @staticmethod
    @abstractmethod
    def get_template_path() -> Path:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_output_path() -> Path:
        raise NotImplementedError

    @staticmethod
    def get_template_config() -> dict:
        return {}

    @classmethod
    @final
    def render_template(cls) -> None:
        template_path = cls.get_template_path()
        if not template_path.is_file():
            raise AssertionError(f"{ template_path }: No such file")

        output_path = cls.get_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open(mode="a+", encoding="utf-8") as fd:
            fd.seek(0)

            loader = FileSystemLoader(template_path.parent)
            env = Environment(loader=loader, keep_trailing_newline=True)
            template = env.get_template(template_path.name)

            template_config = cls.get_template_config()
            rendered_template = template.render(**template_config)

            if rendered_template != fd.read():
                print(f"{ template_path } -> { output_path }")

                fd.seek(0)
                fd.truncate()
                fd.write(rendered_template)


if __name__ == "__main__":
    print("Running generators...")

    def locate_binders() -> Generator[BinderBase, None, None]:
        root = Path(__file__).parent.parent
        pattern = str(Path("*") / "generators" / "*.py")

        for path in root.glob(pattern):
            loader = SourceFileLoader(path.stem, str(path))
            module = loader.load_module()

            yield from (
                cls
                for _, cls in inspect.getmembers(module, predicate=inspect.isclass)
                if cls.__module__ == module.__name__ and issubclass(cls, BinderBase)
            )

    for binder in locate_binders():
        binder.render_template()

    print("OK!")
