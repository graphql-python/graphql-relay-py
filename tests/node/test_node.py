from itertools import chain
from typing import Any, NamedTuple, Optional, Union

from graphql import (
    graphql_sync,
    print_schema,
    GraphQLField,
    GraphQLID,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLSchema,
    GraphQLString,
)

from graphql_relay import node_definitions

from ..utils import dedent


class User(NamedTuple):
    id: str
    name: str


class Photo(NamedTuple):
    id: str
    width: int


user_data = [User(id="1", name="John Doe"), User(id="2", name="Jane Smith")]

photo_data = [Photo(id="3", width=300), Photo(id="4", width=400)]


def get_node(id_: str, info: GraphQLResolveInfo) -> Optional[Union[User, Photo]]:
    assert info.schema is schema
    return next(
        filter(
            lambda obj: obj.id == id_,  # type: ignore
            chain(user_data, photo_data),
        ),
        None,
    )


def get_node_type(
    obj: Union[User, Photo], info: GraphQLResolveInfo, _type: Any
) -> Optional[GraphQLObjectType]:
    assert info.schema is schema
    if obj in user_data:
        return user_type
    if obj in photo_data:
        return photo_type
    return None


node_interface, node_field, nodes_field = node_definitions(get_node, get_node_type)


user_type = GraphQLObjectType(
    "User",
    lambda: {
        "id": GraphQLField(GraphQLNonNull(GraphQLID)),
        "name": GraphQLField(GraphQLString),
    },
    interfaces=[node_interface],
)

photo_type = GraphQLObjectType(
    "Photo",
    lambda: {
        "id": GraphQLField(GraphQLNonNull(GraphQLID)),
        "width": GraphQLField(GraphQLInt),
    },
    interfaces=[node_interface],
)

query_type = GraphQLObjectType(
    "Query", lambda: {"node": node_field, "nodes": nodes_field}
)

schema = GraphQLSchema(query=query_type, types=[node_interface, user_type, photo_type])


def describe_node_interface_and_fields():
    def describe_ability_to_refetch():
        def gets_the_correct_id_for_users():
            source = """
              {
                node(id: "1") {
                  id
                }
              }
            """
            assert graphql_sync(schema, source) == ({"node": {"id": "1"}}, None)

        def gets_the_correct_name_for_users():
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
            assert graphql_sync(schema, source) == (
                {"node": {"id": "1", "name": "John Doe"}},
                None,
            )

        def gets_the_correct_width_for_photos():
            source = """
              {
                node(id: "4") {
                  id
                  ... on Photo {
                    width
                  }
                }
              }
            """
            assert graphql_sync(schema, source) == (
                {"node": {"id": "4", "width": 400}},
                None,
            )

        def gets_the_correct_typename_for_users():
            source = """
              {
                node(id: "1") {
                  id
                  __typename
                }
              }
            """
            assert graphql_sync(schema, source) == (
                {"node": {"id": "1", "__typename": "User"}},
                None,
            )

        def gets_the_correct_typename_for_photos():
            source = """
              {
                node(id: "4") {
                  id
                  __typename
                }
              }
            """
            assert graphql_sync(schema, source) == (
                {"node": {"id": "4", "__typename": "Photo"}},
                None,
            )

        def ignores_photo_fragments_on_user():
            source = """
              {
                node(id: "1") {
                  id
                  ... on Photo {
                    width
                  }
                }
              }
            """
            assert graphql_sync(schema, source) == ({"node": {"id": "1"}}, None)

        def returns_null_for_bad_ids():
            source = """
              {
                node(id: "5") {
                  id
                }
              }
            """
            assert graphql_sync(schema, source) == ({"node": None}, None)

        def returns_nulls_for_bad_ids():
            source = """
              {
                nodes(ids: ["3", "5"]) {
                  id
                }
              }
            """
            assert graphql_sync(schema, source) == (
                {"nodes": [{"id": "3"}, None]},
                None,
            )

    def generates_correct_types():
        assert print_schema(schema).rstrip() == dedent(
            '''
            """An object with an ID"""
            interface Node {
              """The id of the object."""
              id: ID!
            }

            type User implements Node {
              id: ID!
              name: String
            }

            type Photo implements Node {
              id: ID!
              width: Int
            }

            type Query {
              """Fetches an object given its ID"""
              node(
                """The ID of an object"""
                id: ID!
              ): Node

              """Fetches objects given their IDs"""
              nodes(
                """The IDs of objects"""
                ids: [ID!]!
              ): [Node]!
            }
            '''
        )
