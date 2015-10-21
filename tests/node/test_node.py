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

from graphql_relay.node.node import node_definitions

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


def get_node(id, info):
    assert info.schema == schema
    if id in userData:
        return userData[id]
    else:
        return photoData[id]


def get_node_type(obj, info):
    if obj.id in userData:
        return userType
    else:
        return photoType

_node_definitions = node_definitions(get_node, get_node_type)
node_field, node_interface = _node_definitions.node_field, _node_definitions.node_interface

userType = GraphQLObjectType(
    'User',
    fields=lambda: {
        'id': GraphQLField(GraphQLNonNull(GraphQLID)),
        'name': GraphQLField(GraphQLString),
    },
    interfaces=[node_interface]
)

photoType = GraphQLObjectType(
    'Photo',
    fields=lambda: {
        'id': GraphQLField(GraphQLNonNull(GraphQLID)),
        'width': GraphQLField(GraphQLInt),
    },
    interfaces=[node_interface]
)

queryType = GraphQLObjectType(
    'Query',
    fields=lambda: {
        'node': node_field,
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
    assert not result.errors
    assert result.data == expected
