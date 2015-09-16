from collections import namedtuple
from pytest import raises
from graphql.core import graphql
from graphql.core.type import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLArgument,
    GraphQLList,
    GraphQLNonNull,
    GraphQLInt,
    GraphQLString,
    GraphQLBoolean,
    GraphQLID,
)

from graphql_relay.node.node import nodeDefinitions

User = namedtuple('User', ['id', 'name'])
Photo = namedtuple('Photo', ['id', 'width'])

userData = {
    '1': User(id=1, name='John Doe'),
    '2': User(id=2, name='Jane Smith'),
}

photoData = {
    '3': Photo(id=3, width=300),
    '4': Photo(id=4, width=400),
}

def getNode(id, info):
    assert schema == schema
    if id in userData:
        return userData[id]
    else:
        return photoData[id]

def getNodeType(obj):
    if obj.id in userData:
        return userType
    else:
        return photoType

_nodeDefinitions = nodeDefinitions(getNode, getNodeType)
nodeField, nodeInterface = _nodeDefinitions.nodeField, _nodeDefinitions.nodeInterface

userType = GraphQLObjectType(
    'User',
    fields= lambda: {
        'id': GraphQLField(GraphQLNonNull(GraphQLID)),
        'name': GraphQLField(GraphQLString),
    },
    interfaces= [nodeInterface]
)

photoType = GraphQLObjectType(
    'Photo',
    fields= lambda: {
        'id': GraphQLField(GraphQLNonNull(GraphQLID)),
        'width': GraphQLField(GraphQLInt),
    },
    interfaces= [nodeInterface]
)

queryType = GraphQLObjectType(
    'Query',
    fields= lambda: {
        'node': nodeField,
    }
)

schema = GraphQLSchema(query=queryType)

def test_include_connections_and_edge_types():
    query = '''
      {
        node(id: "1") {
          id
        }
      }
    '''
    expected = {
      'node': {
        'id': '1',
      }
    }
    result = graphql(schema, query)
    assert result.errors == None
    assert result.data == expected

