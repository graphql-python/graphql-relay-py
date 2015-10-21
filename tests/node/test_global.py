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


def get_node(global_id, *args):
    resolved_global_id = from_global_id(global_id)
    _type, _id = resolved_global_id.type, resolved_global_id.id
    if _type == 'User':
        return userData[_id]
    else:
        return photoData[_id]


def get_node_type(obj, info):
    if isinstance(obj, User):
        return userType
    else:
        return photoType

_node_definitions = node_definitions(get_node, get_node_type)
node_field, node_interface = _node_definitions.node_field, _node_definitions.node_interface

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
        'id': global_id_field('Photo', lambda obj: obj.photoId),
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
            resolver=lambda *
            _: [userData['1'], userData['2'], photoData['1'], photoData['2']]
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
