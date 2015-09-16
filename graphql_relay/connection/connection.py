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
    def __init__(self, name, nodeType, edgeFields=None, connectionFields=None):
        self.name = name
        self.nodeType = nodeType
        self.edgeFields = edgeFields
        self.connectionFields = connectionFields


class GraphQLConnection(object):
    def __init__(self, edgeType, connectionType):
        self.edgeType = edgeType
        self.connectionType = connectionType


connectionArgs = {
    'before': GraphQLArgument(GraphQLString),
    'after': GraphQLArgument(GraphQLString),
    'first': GraphQLArgument(GraphQLInt),
    'last': GraphQLArgument(GraphQLInt),
}


def resolveMaybeThunk(f):
    if hasattr(f, '__call__'):
        return f()
    return f


def connectionDefinitions(*args, **kwargs):
    if len(args) == 1 and not kwargs and isinstance(args[0], ConnectionConfig):
        config = args[0]
    else:
        config = ConnectionConfig(*args, **kwargs)
    name, nodeType = config.name, config.nodeType
    edgeFields = config.edgeFields or {}
    connectionFields = config.connectionFields or {}
    edgeType = GraphQLObjectType(
        name+'Edge',
        description='An edge in a connection.',
        fields=lambda: dict({
            'node': GraphQLField(
                nodeType,
                description='The item at the end of the edge',
            ),
            'cursor': GraphQLField(
                GraphQLNonNull(GraphQLString),
                description='A cursor for use in pagination',
            )
        }, **resolveMaybeThunk(edgeFields))
    )

    connectionType = GraphQLObjectType(
        name+'Connection',
        description='A connection to a list of items.',
        fields=lambda: dict({
            'pageInfo': GraphQLField(
                GraphQLNonNull(pageInfoType),
                description='The Information to aid in pagination',
            ),
            'edges': GraphQLField(
                GraphQLList(edgeType),
                description='Information to aid in pagination.',
            )
        }, **resolveMaybeThunk(connectionFields))
    )

    return GraphQLConnection(edgeType, connectionType)


# The common page info type used by all connections.

pageInfoType = GraphQLObjectType(
    'PageInfo',
    description='Information about pagination in a connection.',
    fields=lambda:{
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
