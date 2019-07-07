from typing import NamedTuple

from pytest import mark

from graphql import graphql
from graphql.type import (
    GraphQLField,
    GraphQLID,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString)

from graphql_relay import node_definitions


class User(NamedTuple):
    id: str
    name: str


user_data = {
    '1': User(id='1', name='John Doe'),
    '2': User(id='2', name='Jane Smith'),
}

node_interface, node_field = node_definitions(
    lambda id_, _info: user_data[id_], lambda _obj, _info, _type: user_type)[:2]


user_type = GraphQLObjectType(
    'User', lambda: {
        'id': GraphQLField(GraphQLNonNull(GraphQLID)),
        'name': GraphQLField(GraphQLString),
    },
    interfaces=[node_interface]
)

query_type = GraphQLObjectType(
    'Query', lambda: {
        'node': node_field
    }
)

schema = GraphQLSchema(
    query=query_type,
    types=[user_type]
)


@mark.asyncio
async def test_gets_the_correct_id_for_users():
    query = '''
      {
        node(id: "1") {
          id
        }
      }
    '''
    assert await graphql(schema, query) == (
        {
            'node': {'id': '1'}
        },
        None
    )


@mark.asyncio
async def test_gets_the_correct_name_for_users():
    query = '''
      {
        node(id: "1") {
          id
          ... on User {
            name
          }
        }
      }
    '''
    assert await graphql(schema, query) == (
        {
            'node': {'id': '1', 'name': 'John Doe'}
        },
        None
    )
