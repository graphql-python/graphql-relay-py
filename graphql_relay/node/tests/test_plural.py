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

from graphql_relay.node.plural import plural_identifying_root_field

userType = GraphQLObjectType(
    'User',
    fields=lambda: {
        'username': GraphQLField(GraphQLString),
        'url': GraphQLField(GraphQLString),
    }
)
User = namedtuple('User', ['username', 'url'])


queryType = GraphQLObjectType(
    'Query',
    fields=lambda: {
        'usernames': plural_identifying_root_field(
            'usernames',
            description='Map from a username to the user',
            input_type=GraphQLString,
            output_type=userType,
            resolve_single_input=lambda username, context, info: User(
                username=username,
                url='www.facebook.com/' + username + '?lang=' + info.root_value.lang
            )
        )
    }
)

class root_value:
    lang = 'en'

schema = GraphQLSchema(query=queryType)


def test_allows_fetching():
    query = '''
    {
      usernames(usernames:["dschafer", "leebyron", "schrockn"]) {
        username
        url
      }
    }
    '''
    expected = {
        'usernames': [
            {
                'username': 'dschafer',
                'url': 'www.facebook.com/dschafer?lang=en'
            },
            {
                'username': 'leebyron',
                'url': 'www.facebook.com/leebyron?lang=en'
            },
            {
                'username': 'schrockn',
                'url': 'www.facebook.com/schrockn?lang=en'
            },
        ]
    }
    result = graphql(schema, query, root_value=root_value)
    assert not result.errors
    assert result.data == expected


def test_correctly_introspects():
    query = '''
    {
      __schema {
        queryType {
          fields {
            name
            args {
              name
              type {
                kind
                ofType {
                  kind
                  ofType {
                    kind
                    ofType {
                      name
                      kind
                    }
                  }
                }
              }
            }
            type {
              kind
              ofType {
                name
                kind
              }
            }
          }
        }
      }
    }
    '''
    expected = {
        '__schema': {
            'queryType': {
                'fields': [
                    {
                        'name': 'usernames',
                        'args': [
                            {
                                'name': 'usernames',
                                'type': {
                                    'kind': 'NON_NULL',
                                    'ofType': {
                                        'kind': 'LIST',
                                        'ofType': {
                                            'kind': 'NON_NULL',
                                            'ofType': {
                                                'name': 'String',
                                                'kind': 'SCALAR',
                                            }
                                        }
                                    }
                                }
                            }
                        ],
                        'type': {
                            'kind': 'LIST',
                            'ofType': {
                                'name': 'User',
                                'kind': 'OBJECT',
                            }
                        }
                    }
                ]
            }
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected
