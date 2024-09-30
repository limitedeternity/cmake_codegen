from abc import abstractmethod
from argparse import ArgumentParser
import difflib
import glob
import importlib.machinery
import importlib.util
import inspect
from pathlib import Path
import sys
from types import ModuleType
from typing import final, runtime_checkable, Dict, Generator, Optional, Protocol, Tuple

from jinja2 import FileSystemLoader, Environment, StrictUndefined

from _codegen.lib.helpers import unwrap


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
    def render_template(cls, *, return_diff=False) -> Tuple[bool, Optional[str]]:
        template_path = cls.get_template_path()
        if not template_path.is_file():
            raise OSError(f"{ template_path }: No such file")

        output_path = cls.get_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open(mode="a+", encoding="utf-8") as fd:
            fd.seek(0)

            loader = FileSystemLoader(template_path.parent)
            env = Environment(loader=loader, keep_trailing_newline=True, undefined=StrictUndefined)

            template = env.get_template(template_path.name)
            template_config = cls.get_template_config()
            rendered_template = template.render(**template_config)

            if has_changes := (content := fd.read()) != rendered_template:
                fd.seek(0)
                fd.truncate()
                fd.write(rendered_template)

            return has_changes, None if not return_diff else "".join(
                difflib.unified_diff(
                    content.splitlines(True),
                    rendered_template.splitlines(True),
                    f"{ output_path } (Original)",
                    f"{ template_path } (Rendered)",
                )
            )


class Action(Protocol):
    @staticmethod
    @abstractmethod
    def execute(binder: BinderBase) -> None:
        raise NotImplementedError


class ActionFactory:
    registered_actions: Dict[str, Action] = {}

    @classmethod
    def make_action(cls, action: str) -> Action:
        try:
            return cls.registered_actions[action]

        except KeyError as err:
            raise NotImplementedError(f"{action=} isn't registered") from err

    @classmethod
    def register(cls, action: str):
        def wrapper(obj: Action) -> Action:
            cls.registered_actions[action] = obj
            return obj

        return wrapper


if __name__ == "__main__":

    @ActionFactory.register("generate")
    class GenerateAction(Action):
        @staticmethod
        def execute(binder: BinderBase) -> None:
            template_path = binder.get_template_path()
            output_path = binder.get_output_path()

            has_changes, render_diff = binder.render_template(return_diff=args.with_diff)

            if has_changes and not args.with_diff:
                print(f"Generated: { template_path } -> { output_path }")

            elif has_changes and args.with_diff:
                print(render_diff)

    @ActionFactory.register("nuke")
    class NukeAction(Action):
        @staticmethod
        def execute(binder: BinderBase) -> None:
            output_path = binder.get_output_path()

            if output_path.is_file():
                output_path.unlink(missing_ok=True)
                print(f"Removed: { output_path }")

    parser = ArgumentParser(prog=__package__)
    subparsers = parser.add_subparsers(dest="action", required=True)

    generate_parser = subparsers.add_parser("generate", help="perform code generation")
    nuke_parser = subparsers.add_parser("nuke", help="remove every generated file")

    generate_parser.add_argument(
        "--with-diff",
        dest="with_diff",
        default=False,
        action="store_true",
        help="show generation deltas",
    )

    args = parser.parse_args()

    def load_module(path: Path) -> ModuleType:
        loader_args = (path.stem, str(path))

        loader = importlib.machinery.SourceFileLoader(*loader_args)
        spec = importlib.util.spec_from_file_location(*loader_args, loader=loader)
        module = importlib.util.module_from_spec(unwrap(spec))

        sys.modules[module.__name__] = module
        loader.exec_module(module)

        return module

    def locate_binders() -> Generator[BinderBase, None, None]:
        root = Path(__file__).parent.parent
        pattern = Path("**") / "generators" / "*.py"

        for path in map(Path, glob.iglob(str(root / pattern), recursive=True)):
            module = load_module(path)

            yield from (
                cls
                for _, cls in inspect.getmembers(module, predicate=inspect.isclass)
                if cls.__module__ == module.__name__ and issubclass(cls, BinderBase)
            )

    def drain(genex) -> None:
        for _ in genex:
            ...

    print("Running generators...")

    action_obj = ActionFactory.make_action(args.action)
    drain(map(action_obj.execute, locate_binders()))

    print("OK!")
