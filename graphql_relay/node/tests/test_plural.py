from collections import namedtuple

from pytest import mark

from graphql import graphql
from graphql.type import (
    GraphQLField,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString)

from graphql_relay import plural_identifying_root_field

userType = GraphQLObjectType(
    'User',
    fields=lambda: {
        'username': GraphQLField(GraphQLString),
        'url': GraphQLField(GraphQLString),
    }
)
User = namedtuple('User', ['username', 'url'])


def resolve_single_input(info, username):
    assert info.schema is schema
    url = f'www.facebook.com/{username}?lang={info.root_value.lang}'
    return User(username=username, url=url)


queryType = GraphQLObjectType(
    'Query', lambda: {
        'usernames':  plural_identifying_root_field(
            'usernames',
            description='Map from a username to the user',
            input_type=GraphQLString,
            output_type=userType,
            resolve_single_input=resolve_single_input)})

schema = GraphQLSchema(query=queryType)

RootValue = namedtuple('RootValue', ['lang'])

root_value = RootValue(lang='en')


@mark.asyncio
async def test_allows_fetching():
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
    result = await graphql(schema, query, root_value=root_value)
    assert not result.errors
    assert result.data == expected


@mark.asyncio
async def test_correctly_introspects():
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
    result = await graphql(schema, query)
    assert not result.errors
    assert result.data == expected
