from typing import Any, Dict, List, NamedTuple, Optional

__all__ = [
    'Connection', 'ConnectionArguments', 'ConnectionCursor', 'Edge', 'PageInfo'
]


"""A type alias for cursors in this implementation."""
ConnectionCursor = str


class PageInfo(NamedTuple):
    """A type designed to be exposed as `PageInfo` over GraphQL."""

    startCursor: Optional[ConnectionCursor]
    endCursor: Optional[ConnectionCursor]
    hasPreviousPage: Optional[bool]
    hasNextPage: Optional[bool]


class Edge(NamedTuple):
    """A type designed to be exposed as a `Edge` over GraphQL."""

    node: Any
    cursor: ConnectionCursor


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
