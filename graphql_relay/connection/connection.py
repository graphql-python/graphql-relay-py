from graphql.core.type import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLList,
    GraphQLObjectType,
    GraphQLString,
    GraphQLField
)


class ConnectionConfig(object):

    '''
    Returns a GraphQLFieldConfigArgumentMap appropriate to include
    on a field whose return type is a connection type.
    '''

    def __init__(self, name, node_type, edge_fields=None, connection_fields=None):
        self.name = name
        self.node_type = node_type
        self.edge_fields = edge_fields
        self.connection_fields = connection_fields


class GraphQLConnection(object):

    def __init__(self, edge_type, connection_type):
        self.edge_type = edge_type
        self.connection_type = connection_type


connectionArgs = {
    'before': GraphQLArgument(GraphQLString),
    'after': GraphQLArgument(GraphQLString),
    'first': GraphQLArgument(GraphQLInt),
    'last': GraphQLArgument(GraphQLInt),
}


def resolve_maybe_thunk(f):
    if hasattr(f, '__call__'):
        return f()
    return f


def connection_definitions(*args, **kwargs):
    if len(args) == 1 and not kwargs and isinstance(args[0], ConnectionConfig):
        config = args[0]
    else:
        config = ConnectionConfig(*args, **kwargs)
    name, node_type = config.name, config.node_type
    edge_fields = config.edge_fields or {}
    connection_fields = config.connection_fields or {}
    edge_type = GraphQLObjectType(
        name + 'Edge',
        description='An edge in a connection.',
        fields=lambda: dict({
            'node': GraphQLField(
                node_type,
                description='The item at the end of the edge',
            ),
            'cursor': GraphQLField(
                GraphQLNonNull(GraphQLString),
                description='A cursor for use in pagination',
            )
        }, **resolve_maybe_thunk(edge_fields))
    )

    connection_type = GraphQLObjectType(
        name + 'Connection',
        description='A connection to a list of items.',
        fields=lambda: dict({
            'pageInfo': GraphQLField(
                GraphQLNonNull(page_info_type),
                description='The Information to aid in pagination',
            ),
            'edges': GraphQLField(
                GraphQLList(edge_type),
                description='Information to aid in pagination.',
            )
        }, **resolve_maybe_thunk(connection_fields))
    )

    return GraphQLConnection(edge_type, connection_type)


# The common page info type used by all connections.

page_info_type = GraphQLObjectType(
    'PageInfo',
    description='Information about pagination in a connection.',
    fields=lambda: {
        'hasNextPage': GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description='When paginating forwards, are there more items?',
        ),
        'hasPreviousPage': GraphQLField(
            GraphQLNonNull(GraphQLBoolean),
            description='When paginating backwards, are there more items?',
        ),
        'startCursor': GraphQLField(
            GraphQLString,
            description='When paginating backwards, the cursor to continue.',
        ),
        'endCursor': GraphQLField(
            GraphQLString,
            description='When paginating forwards, the cursor to continue.',
        ),
    }
)
