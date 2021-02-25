from typing import Any, Dict, List, NamedTuple, Optional

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

__all__ = ["Connection", "ConnectionArguments", "ConnectionCursor", "Edge", "PageInfo"]


"""A type alias for cursors in this implementation."""
ConnectionCursor = str


class PageInfoType(Protocol):
    @property
    def startCursor(self) -> Optional[ConnectionCursor]:
        ...

    def endCursor(self) -> Optional[ConnectionCursor]:
        ...

    def hasPreviousPage(self) -> Optional[bool]:
        ...

    def hasNextPage(self) -> Optional[bool]:
        ...


class PageInfoConstructor(Protocol):
    def __call__(
        self,
        *,
        startCursor: Optional[ConnectionCursor],
        endCursor: Optional[ConnectionCursor],
        hasPreviousPage: Optional[bool],
        hasNextPage: Optional[bool],
    ) -> PageInfoType:
        ...


class PageInfo(NamedTuple):
    """A type designed to be exposed as `PageInfo` over GraphQL."""

    startCursor: Optional[ConnectionCursor]
    endCursor: Optional[ConnectionCursor]
    hasPreviousPage: Optional[bool]
    hasNextPage: Optional[bool]


class EdgeType(Protocol):
    @property
    def node(self) -> Any:
        ...

    @property
    def cursor(self) -> ConnectionCursor:
        ...


class EdgeConstructor(Protocol):
    def __call__(self, *, node: Any, cursor: ConnectionCursor) -> EdgeType:
        ...


class Edge(NamedTuple):
    """A type designed to be exposed as a `Edge` over GraphQL."""

    node: Any
    cursor: ConnectionCursor


class ConnectionType(Protocol):
    @property
    def edges(self):
        List[EdgeType]: ...

    @property
    def pageInfo(self):
        PageInfoType: ...


class ConnectionConstructor(Protocol):
    def __call__(
        self,
        *,
        edges: List[EdgeType],
        pageInfo: PageInfoType,
    ) -> ConnectionType:
        ...


class Connection(NamedTuple):
    """A type designed to be exposed as a `Connection` over GraphQL."""

    edges: List[Edge]
    pageInfo: PageInfo


"""A type describing the arguments a connection field receives in GraphQL.

The following kinds of arguments are expected (all optional):

    before: ConnectionCursor
    after: ConnectionCursor
    first: int
    last: int
"""
ConnectionArguments = Dict[str, Any]
