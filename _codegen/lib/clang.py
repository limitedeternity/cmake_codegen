import clang.cindex as cl
from dataclasses import dataclass
from typing import Generator, Iterable, List

from _codegen.lib.helpers import return_on_failure


@dataclass
class Locator:
    iterable: Iterable[cl.Cursor]

    @classmethod
    def take_all_nodes(cls, cursor: cl.Cursor):
        return cls(cursor.walk_preorder())

    @classmethod
    def take_child_nodes(cls, cursor: cl.Cursor):
        return cls(cursor.get_children())

    def locate(self, *kinds: cl.CursorKind) -> Generator[cl.Cursor, None, None]:
        yield from filter(
            return_on_failure(False)(lambda cur: cur.kind in kinds), self.iterable
        )


@dataclass
class Node:
    cursor: cl.Cursor

    def has_annotation(self, spelling: str) -> bool:
        return any(
            map(
                lambda cur: cur.spelling == spelling,
                Locator.take_child_nodes(self.cursor).locate(
                    cl.CursorKind.ANNOTATE_ATTR
                ),
            )
        )

    @property
    def fully_qualified_name(self) -> str:
        def scope_components(cur: cl.Cursor) -> List[str]:
            parent = cur.lexical_parent

            if parent.kind.is_declaration():
                return scope_components(parent) + [parent.spelling]

            return []

        return "::".join(scope_components(self.cursor) + [self.cursor.spelling])
