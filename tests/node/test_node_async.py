from typing import NamedTuple

from pytest import mark

from graphql import (
    graphql,
    GraphQLField,
    GraphQLID,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
)

from graphql_relay import node_definitions


class User(NamedTuple):
    id: str
    name: str


user_data = [User(id="1", name="John Doe"), User(id="2", name="Jane Smith")]

user_type: GraphQLObjectType

node_interface, node_field = node_definitions(
    lambda id_, _info: next(filter(lambda obj: obj.id == id_, user_data), None),
    lambda _obj, _info, _type: user_type.name,
)[:2]


user_type = GraphQLObjectType(
    "User",
    lambda: {
        "id": GraphQLField(GraphQLNonNull(GraphQLID)),
        "name": GraphQLField(GraphQLString),
    },
    interfaces=[node_interface],
)

query_type = GraphQLObjectType("Query", lambda: {"node": node_field})

schema = GraphQLSchema(query=query_type, types=[user_type])


def describe_node_interface_and_fields_with_async_object_fetcher():
    @mark.asyncio
    async def gets_the_correct_id_for_users():
        source = """
          {
            node(id: "1") {
              id
            }
          }
        """
        assert await graphql(schema, source) == ({"node": {"id": "1"}}, None)

    @mark.asyncio
    async def gets_the_correct_name_for_users():
        source = """
          {
            node(id: "1") {
              id
              ... on User {
                name
              }
            }
          }
        """
        assert await graphql(schema, source) == (
            {"node": {"id": "1", "name": "John Doe"}},
            None,
        )
