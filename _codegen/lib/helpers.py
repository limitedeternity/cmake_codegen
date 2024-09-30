import functools
import operator
from pathlib import Path
from typing import TypeVar, Callable, Optional

_T = TypeVar("_T")


def return_on_failure(value):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except:
                return value

        return wrapper

    return decorator


def unwrap(obj: Optional[_T]) -> _T:
    assert obj is not None
    return obj


def detect_line_ending(file_path: Path) -> str:
    endings = {"\r\n": 0, "\r": 0, "\n": 0}

    with file_path.open(mode="r", encoding="utf-8") as fd:
        for line in fd:
            if line.endswith("\r\n"):
                endings["\r\n"] += 1

            elif line.endswith("\r"):
                endings["\r"] += 1

            elif line.endswith("\n"):
                endings["\n"] += 1

    return max(endings, key=endings.get)


def repeat_access(init: _T, attr: str, times: int) -> _T:
    accessor: Callable[[_T], _T] = operator.attrgetter(attr)
    return functools.reduce(lambda acc, _: accessor(acc), range(times), init)
