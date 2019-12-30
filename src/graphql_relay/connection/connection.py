from typing import Any, NamedTuple

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

__all__ = [
    "connection_definitions",
    "forward_connection_args",
    "backward_connection_args",
    "connection_args",
    "GraphQLConnectionDefinitions",
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
                description="The Information to aid in pagination",
            ),
            "edges": GraphQLField(
                GraphQLList(edge_type), description="A list of edges."
            ),
            **resolve_maybe_thunk(connection_fields),
        },
    )

    return GraphQLConnectionDefinitions(edge_type, connection_type)


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
