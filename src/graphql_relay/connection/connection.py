from typing import Any, Dict, List, NamedTuple, Optional

from graphql.type import (
    GraphQLArgument,
    GraphQLArgumentMap,
    GraphQLBoolean,
    GraphQLField,
    GraphQLFieldMap,
    GraphQLFieldResolver,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
    Thunk,
)

try:
    from typing import Protocol
except ImportError:  # Python < 3.8
    from typing_extensions import Protocol  # type: ignore

__all__ = [
    "connection_definitions",
    "forward_connection_args",
    "backward_connection_args",
    "connection_args",
    "Connection",
    "ConnectionArguments",
    "ConnectionCursor",
    "Edge",
    "GraphQLConnectionDefinitions",
    "PageInfo",
]


# Returns a GraphQLArgumentMap appropriate to include on a field
# whose return type is a connection type with forward pagination.
forward_connection_args: GraphQLArgumentMap = {
    "after": GraphQLArgument(GraphQLString),
    "first": GraphQLArgument(GraphQLInt),
}

# Returns a GraphQLArgumentMap appropriate to include on a field
# whose return type is a connection type with backward pagination.
backward_connection_args: GraphQLArgumentMap = {
    "before": GraphQLArgument(GraphQLString),
    "last": GraphQLArgument(GraphQLInt),
}

# Returns a GraphQLArgumentMap appropriate to include on a field
# whose return type is a connection type with bidirectional pagination.
connection_args = {**forward_connection_args, **backward_connection_args}


class GraphQLConnectionDefinitions(NamedTuple):
    edge_type: GraphQLObjectType
    connection_type: GraphQLObjectType


def resolve_maybe_thunk(thing_or_thunk: Thunk) -> Any:
    return thing_or_thunk() if callable(thing_or_thunk) else thing_or_thunk


"""A type alias for cursors in this implementation."""
ConnectionCursor = str


"""A type describing the arguments a connection field receives in GraphQL.

The following kinds of arguments are expected (all optional):

    before: ConnectionCursor
    after: ConnectionCursor
    first: int
    last: int
"""
ConnectionArguments = Dict[str, Any]


def connection_definitions(
    node_type: GraphQLObjectType,
    name: str = None,
    resolve_node: GraphQLFieldResolver = None,
    resolve_cursor: GraphQLFieldResolver = None,
    edge_fields: Thunk[GraphQLFieldMap] = None,
    connection_fields: Thunk[GraphQLFieldMap] = None,
) -> GraphQLConnectionDefinitions:
    """Return GraphQLObjectTypes for a connection with the given name.

    The nodes of the returned object types will be of the specified type.
    """
    name = name or node_type.name
    edge_fields = edge_fields or {}
    connection_fields = connection_fields or {}

    edge_type = GraphQLObjectType(
        name + "Edge",
        description="An edge in a connection.",
        fields=lambda: {
            "node": GraphQLField(
                node_type,
                resolve=resolve_node,
                description="The item at the end of the edge",
            ),
            "cursor": GraphQLField(
                GraphQLNonNull(GraphQLString),
                resolve=resolve_cursor,
                description="A cursor for use in pagination",
            ),
            **resolve_maybe_thunk(edge_fields),
        },
    )

    connection_type = GraphQLObjectType(
        name + "Connection",
        description="A connection to a list of items.",
        fields=lambda: {
            "pageInfo": GraphQLField(
                GraphQLNonNull(page_info_type),
                description="Information to aid in pagination.",
            ),
            "edges": GraphQLField(
                GraphQLList(edge_type), description="A list of edges."
            ),
            **resolve_maybe_thunk(connection_fields),
        },
    )

    return GraphQLConnectionDefinitions(edge_type, connection_type)


class PageInfoType(Protocol):
    @property
    def startCursor(self) -> Optional[ConnectionCursor]:
        ...

    def endCursor(self) -> Optional[ConnectionCursor]:
        ...

    def hasPreviousPage(self) -> bool:
        ...

    def hasNextPage(self) -> bool:
        ...


class PageInfoConstructor(Protocol):
    def __call__(
        self,
        *,
        startCursor: Optional[ConnectionCursor],
        endCursor: Optional[ConnectionCursor],
        hasPreviousPage: bool,
        hasNextPage: bool,
    ) -> PageInfoType:
        ...


class PageInfo(NamedTuple):
    """A type designed to be exposed as `PageInfo` over GraphQL."""

    startCursor: Optional[ConnectionCursor]
    endCursor: Optional[ConnectionCursor]
    hasPreviousPage: bool
    hasNextPage: bool


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


# The common page info type used by all connections.
page_info_type = GraphQLObjectType(
    "PageInfo",
    description="Information about pagination in a connection.",
    fields=lambda: {
        "hasNextPage": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="When paginating forwards, are there more items?",
        ),
        "hasPreviousPage": GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description="When paginating backwards, are there more items?",
        ),
        "startCursor": GraphQLField(
            GraphQLString,
            description="When paginating backwards, the cursor to continue.",
        ),
        "endCursor": GraphQLField(
            GraphQLString,
            description="When paginating forwards, the cursor to continue.",
        ),
    },
)
