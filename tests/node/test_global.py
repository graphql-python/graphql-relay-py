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

from graphql_relay.node.node import (
  fromGlobalId,
  globalIdField,
  nodeDefinitions,
)

User = namedtuple('User', ['id', 'name'])
Photo = namedtuple('Photo', ['photoId', 'width'])

userData = {
  '1': User(id=1, name='John Doe'),
  '2': User(id=2, name='Jane Smith'),
}

photoData = {
  '1': Photo(photoId=1, width=300),
  '2': Photo(photoId=2, width=400),
}

def getNode(globalId):
  resolvedGlobalId = fromGlobalId(globalId)
  _type, _id = resolvedGlobalId.type, resolvedGlobalId.id
  if type == 'User':
    return userData[id]
  else:
    return photoData[id]

def getNodeType(obj):
  if hasattr(obj, 'id'):
    return userType
  else:
    return photoType

_nodeDefinitions = nodeDefinitions(getNode, getNodeType)
nodeField, nodeInterface = _nodeDefinitions.nodeField, _nodeDefinitions.nodeInterface

userType = GraphQLObjectType(
  'User',
  fields= lambda: {
    'id': globalIdField('User'),
    'name': GraphQLField(GraphQLString),
  },
  interfaces= [nodeInterface]
)

photoType = GraphQLObjectType(
  'Photo',
  fields= lambda: {
    'id': globalIdField('Photo', lambda obj: obj.photoId),
    'width': GraphQLField(GraphQLInt),
  },
  interfaces= [nodeInterface]
)

queryType = GraphQLObjectType(
  'Query',
  fields= lambda: {
    'node': nodeField,
    'allObjects': GraphQLField(
      GraphQLList(nodeInterface),
      resolver= lambda *_: [userData['1'], userData['2'], photoData['1'], photoData['2']]
    )
  }
)

schema = GraphQLSchema(query=queryType)

def test_gives_different_ids():
    query = '''
    {
      allObjects {
        id
      }
    }
    '''
    expected = {
      'allObjects': [
        {
          'id': 'VXNlcjox'
        },
        {
          'id': 'VXNlcjoy'
        },
        {
          'id': 'UGhvdG86MQ=='
        },
        {
          'id': 'UGhvdG86Mg=='
        },
      ]
    };
    result = graphql(schema, query)
    assert result.errors == None
    assert result.data == expected
