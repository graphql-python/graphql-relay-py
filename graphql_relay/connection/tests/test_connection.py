from collections import namedtuple
from pytest import raises
from graphql import graphql
from graphql.type import (
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

from ..arrayconnection import connection_from_list
from ..connection import (
    connection_args,
    connection_definitions
)

User = namedtuple('User', ['name', 'friends'])

allUsers = [
    User(name='Dan', friends=[1, 2, 3, 4]),
    User(name='Nick', friends=[0, 2, 3, 4]),
    User(name='Lee', friends=[0, 1, 3, 4]),
    User(name='Joe', friends=[0, 1, 2, 4]),
    User(name='Tim', friends=[0, 1, 2, 3]),
]

userType = GraphQLObjectType(
    'User',
    fields=lambda: {
        'name': GraphQLField(GraphQLString),
        'friends': GraphQLField(
            friendConnection,
            args=connection_args,
            resolver=lambda user, args, *
            _: connection_from_list(user.friends, args),
        ),
    },
)

friendEdge, friendConnection = connection_definitions(
    'Friend',
    userType,
    resolve_node=lambda edge, *_: allUsers[edge.node],
    edge_fields=lambda: {
        'friendshipTime': GraphQLField(
            GraphQLString,
            resolver=lambda *_: 'Yesterday'
        ),
    },
    connection_fields=lambda: {
        'totalCount': GraphQLField(
            GraphQLInt,
            resolver=lambda *_: len(allUsers) - 1
        ),
    }
)

queryType = GraphQLObjectType(
    'Query',
    fields=lambda: {
        'user': GraphQLField(
            userType,
            resolver=lambda *_: allUsers[0]
        ),
    }
)

schema = GraphQLSchema(query=queryType)


def test_include_connections_and_edge_types():
    query = '''
      query FriendsQuery {
        user {
          friends(first: 2) {
            totalCount
            edges {
              friendshipTime
              node {
                name
              }
            }
          }
        }
      }
    '''
    expected = {
        'user': {
            'friends': {
                'totalCount': 4,
                'edges': [
                    {
                        'friendshipTime': 'Yesterday',
                        'node': {
                            'name': 'Nick'
                        }
                    },
                    {
                        'friendshipTime': 'Yesterday',
                        'node': {
                            'name': 'Lee'
                        }
                    },
                ]
            }
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_works_with_forward_connection_args():
    query = '''
      query FriendsQuery {
        user {
          friendsForward: friends(first: 2) {
            edges {
              node {
                name
              }
            }
          }
        }
      }
    '''
    expected = {
        'user': {
            'friendsForward': {
                'edges': [
                    {
                        'node': {
                            'name': 'Nick'
                        }
                    },
                    {
                        'node': {
                            'name': 'Lee'
                        }
                    },
                ]
            }
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_works_with_backward_connection_args():
    query = '''
      query FriendsQuery {
        user {
          friendsBackward: friends(last: 2) {
            edges {
              node {
                name
              }
            }
          }
        }
      }
    '''
    expected = {
        'user': {
            'friendsBackward': {
                'edges': [
                    {
                        'node': {
                            'name': 'Joe'
                        }
                    },
                    {
                        'node': {
                            'name': 'Tim'
                        }
                    },
                ]
            }
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected
