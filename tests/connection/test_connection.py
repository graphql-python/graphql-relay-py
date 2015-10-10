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

from graphql_relay.connection.arrayconnection import connection_from_list
from graphql_relay.connection.connection import (
    connectionArgs,
    connection_definitions
)

User = namedtuple('User', ['name'])

allUsers = [
    User(name='Dan'),
    User(name='Nick'),
    User(name='Lee'),
    User(name='Joe'),
    User(name='Tim'),
]

userType = GraphQLObjectType(
    'User',
    fields=lambda: {
        'name': GraphQLField(GraphQLString),
        'friends': GraphQLField(
            friendConnection,
            args=connectionArgs,
            resolver=lambda user, args, *
            _: connection_from_list(allUsers, args),
        ),
    },
)

friendConnection = connection_definitions(
    'Friend',
    userType,
    edge_fields=lambda: {
        'friendshipTime': GraphQLField(
            GraphQLString,
            resolver=lambda *_: 'Yesterday'
        ),
    },
    connection_fields=lambda: {
        'totalCount': GraphQLField(
            GraphQLInt,
            resolver=lambda *_: len(allUsers)
        ),
    }
).connection_type

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
                'totalCount': 5,
                'edges': [
                    {
                        'friendshipTime': 'Yesterday',
                        'node': {
                            'name': 'Dan'
                        }
                    },
                    {
                        'friendshipTime': 'Yesterday',
                        'node': {
                            'name': 'Nick'
                        }
                    },
                ]
            }
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected
