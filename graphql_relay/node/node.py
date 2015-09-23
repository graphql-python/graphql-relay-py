from graphql_relay.utils import base64, unbase64

from graphql.core.type import (
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLID,
    GraphQLField,
    GraphQLObjectType,
    GraphQLInterfaceType,
)


class GraphQLNode(object):
    def __init__(self, nodeInterface, nodeField):
        self.nodeInterface = nodeInterface
        self.nodeField = nodeField


def nodeDefinitions(idFetcher, typeResolver=None):
    '''
    Given a function to map from an ID to an underlying object, and a function
    to map from an underlying object to the concrete GraphQLObjectType it
    corresponds to, constructs a `Node` interface that objects can implement,
    and a field config for a `node` root field.

    If the typeResolver is omitted, object resolution on the interface will be
    handled with the `isTypeOf` method on object types, as with any GraphQL
    interface without a provided `resolveType` method.
    '''
    nodeInterface = GraphQLInterfaceType(
        'Node',
        description= 'An object with an ID',
        fields= lambda:{
            'id': GraphQLField(
                GraphQLNonNull(GraphQLID),
                description='The id of the object.',
            ),
        },
        resolve_type= typeResolver
    )
    nodeField = GraphQLField(
        nodeInterface,
        description= 'Fetches an object given its ID',
        args= {
            'id': GraphQLArgument(
                GraphQLNonNull(GraphQLID),
                description='The ID of an object'
            )
        },
        resolver= lambda obj, args, info: idFetcher(args.get('id'), info)
    )
    return GraphQLNode(nodeInterface, nodeField)


class ResolvedGlobalId(object):
    def __init__(self, type, id):
        self.type = type
        self.id = id


def toGlobalId(type, id):
    '''
    Takes a type name and an ID specific to that type name, and returns a
    "global ID" that is unique among all types.
    '''
    return base64(':'.join([type, str(id)]))

def fromGlobalId(globalId):
    '''
    Takes the "global ID" created by toGlobalID, and retuns the type name and ID
    used to create it.
    '''
    unbasedGlobalId = unbase64(globalId)
    _type, _id = unbasedGlobalId.split(':', 1)
    return ResolvedGlobalId(_type, _id)


def globalIdField(typeName, idFetcher=None):
    '''
    Creates the configuration for an id field on a node, using `toGlobalId` to
    construct the ID from the provided typename. The type-specific ID is fetcher
    by calling idFetcher on the object, or if not provided, by accessing the `id`
    property on the object.
    '''
    return GraphQLField(
        GraphQLNonNull(GraphQLID),
        description= 'The ID of an object',
        resolver= lambda obj, *_: toGlobalId(typeName, idFetcher(obj) if idFetcher else obj.id)
    )
