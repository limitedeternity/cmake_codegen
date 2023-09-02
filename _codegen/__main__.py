from abc import abstractmethod
from importlib.machinery import SourceFileLoader
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
            raise AssertionError(f"{ str(template_path) }: No such file")

        output_path = cls.get_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open(mode="w", encoding="utf-8") as out:
            loader = FileSystemLoader(template_path.parent)
            env = Environment(loader=loader, keep_trailing_newline=True)
            template = env.get_template(template_path.name)

            template_config = cls.get_template_config()
            rendered_template = template.render(**template_config)
            out.write(rendered_template)


if __name__ == "__main__":
    print("Running generators...")

    def locate_binders() -> Generator[BinderBase, None, None]:
        root = Path(__file__).parent.parent
        pattern = str(Path("*") / "generators" / "*.py")
        class_name = "TemplateBinder"

        for path in root.glob(pattern):
            loader = SourceFileLoader(path.stem, str(path))
            module = loader.load_module()
            binder_class = module.__dict__.get(class_name, None)

            if not binder_class:
                raise AssertionError(
                    f"{ str(path) }: Unable to find <class '{ class_name }'>"
                )

            if not issubclass(binder_class, BinderBase):
                raise AssertionError(
                    f"{ str(path) }: <class '{ class_name }'> is expected to subclass BinderBase"
                )

            yield binder_class

    for binder in locate_binders():
        binder.render_template()

    print("OK!")
