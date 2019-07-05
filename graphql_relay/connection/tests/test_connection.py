from collections import namedtuple

from graphql import graphql
from graphql.type import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLInt,
    GraphQLString,
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
            resolver=lambda user, _info, **args:
            connection_from_list(user.friends, args),
        ),
    },
)

friendEdge, friendConnection = connection_definitions(
    'Friend',
    userType,
    resolve_node=lambda edge, _info: allUsers[edge.node],
    edge_fields=lambda: {
        'friendshipTime': GraphQLField(
            GraphQLString,
            resolver=lambda _user, _info: 'Yesterday'
        ),
    },
    connection_fields=lambda: {
        'totalCount': GraphQLField(
            GraphQLInt,
            resolver=lambda _user, _info: len(allUsers) - 1
        ),
    }
)

queryType = GraphQLObjectType(
    'Query',
    fields=lambda: {
        'user': GraphQLField(
            userType,
            resolver=lambda _root, _info: allUsers[0]
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
