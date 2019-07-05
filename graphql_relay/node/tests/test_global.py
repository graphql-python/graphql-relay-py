from collections import namedtuple
from graphql import graphql
from graphql.type import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLList,
    GraphQLInt,
    GraphQLString,
)

from graphql_relay.node.node import (
    from_global_id,
    global_id_field,
    node_definitions,
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


def get_node(global_id, _info):
    _type, _id = from_global_id(global_id)
    if _type == 'User':
        return userData[_id]
    else:
        return photoData[_id]


def get_node_type(obj, _info):
    if isinstance(obj, User):
        return userType
    else:
        return photoType


node_interface, node_field = node_definitions(get_node, get_node_type)

userType = GraphQLObjectType(
    'User',
    fields=lambda: {
        'id': global_id_field('User'),
        'name': GraphQLField(GraphQLString),
    },
    interfaces=[node_interface]
)

photoType = GraphQLObjectType(
    'Photo',
    fields=lambda: {
        'id': global_id_field('Photo', lambda obj, *_: obj.photoId),
        'width': GraphQLField(GraphQLInt),
    },
    interfaces=[node_interface]
)

queryType = GraphQLObjectType(
    'Query',
    fields=lambda: {
        'node': node_field,
        'allObjects': GraphQLField(
            GraphQLList(node_interface),
            resolver=lambda _root, _info:
                [userData['1'], userData['2'], photoData['1'], photoData['2']]
        )
    }
)

schema = GraphQLSchema(
    query=queryType,
    types=[userType, photoType]
)


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
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_refetches_the_ids():
    query = '''
    {
      user: node(id: "VXNlcjox") {
        id
        ... on User {
          name
        }
      },
      photo: node(id: "UGhvdG86MQ==") {
        id
        ... on Photo {
          width
        }
      }
    }
    '''
    expected = {
        'user': {
            'id': 'VXNlcjox',
            'name': 'John Doe'
        },
        'photo': {
            'id': 'UGhvdG86MQ==',
            'width': 300
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected
