import json
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
    assert info.schema == schema
    if id in userData:
        return userData[id]
    else:
        return photoData[id]

def getNodeType(obj):
    if str(obj.id) in userData:
        return userType
    else:
        return photoType

_nodeDefinitions = nodeDefinitions(getNode, getNodeType)
nodeField, nodeInterface = _nodeDefinitions.nodeField, _nodeDefinitions.nodeInterface

userType = GraphQLObjectType(
    'User',
    fields= lambda: {
        'id': GraphQLField(GraphQLNonNull(GraphQLID)),
        'name': GraphQLField(GraphQLString, resolver=lambda *_: 'name'),
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
        'user': GraphQLField(userType, resolver=lambda *_: userData['1']),
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


def test_preserves_order1():
    query = '''
      {
        node(id: "1") {
          ... on User {
            name
            id
          }
        }
      }
    '''
    result = graphql(schema, query)
    assert not result.errors
    assert json.dumps(result.data) == '{"node": {"name": "name", "id": "1"}}'


def test_preserves_order2():
    query = '''
      {
        node(id: "1") {
          ... on User {
            id
            name
          }
        }
      }
    '''
    result = graphql(schema, query)
    assert not result.errors
    assert json.dumps(result.data) == '{"node": {"id": "1", "name": "name"}}'


def test_preserves_order_general1():
    query = '''
      {
        user {
            id
            name
        }
      }
    '''
    result = graphql(schema, query)
    assert not result.errors
    assert json.dumps(result.data) == '{"user": {"id": "1", "name": "name"}}'


def test_preserves_order_general2():
    query = '''
      {
        user {
            name
            id
        }
      }
    '''
    result = graphql(schema, query)
    assert not result.errors
    assert json.dumps(result.data) == '{"user": {"name": "name", "id": "1"}}'
