from typing import Any, NamedTuple, Optional, Union

from graphql import graphql_sync as graphql
from graphql.type import (
    GraphQLField,
    GraphQLID,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLSchema,
    GraphQLString,
)

from graphql_relay import node_definitions, to_global_id, from_global_id


class User(NamedTuple):
    id: str
    name: str


class Photo(NamedTuple):
    id: str
    width: int


user_data = {"1": User(id="1", name="John Doe"), "2": User(id="2", name="Jane Smith")}

photo_data = {"3": Photo(id="3", width=300), "4": Photo(id="4", width=400)}


def get_node(id_: str, info: GraphQLResolveInfo) -> Optional[Union[User, Photo]]:
    assert info.schema is schema
    if id_ in user_data:
        return user_data[id_]
    if id_ in photo_data:
        return photo_data[id_]
    return None


def get_node_type(
    obj: Union[User, Photo], info: GraphQLResolveInfo, _type: Any
) -> Optional[GraphQLObjectType]:
    assert info.schema is schema
    if obj.id in user_data:
        return user_type
    if obj.id in photo_data:
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

schema = GraphQLSchema(query=query_type, types=[user_type, photo_type])


def describe_node_interface_and_fields():
    def describe_refetchability():
        def gets_the_correct_id_for_users():
            query = """
              {
                node(id: "1") {
                  id
                }
              }
            """
            assert graphql(schema, query) == ({"node": {"id": "1"}}, None)

        def gets_the_correct_name_for_users():
            query = """
              {
                node(id: "1") {
                  id
                  ... on User {
                    name
                  }
                }
              }
            """
            assert graphql(schema, query) == (
                {"node": {"id": "1", "name": "John Doe"}},
                None,
            )

        def gets_the_correct_width_for_photos():
            query = """
              {
                node(id: "4") {
                  id
                  ... on Photo {
                    width
                  }
                }
              }
            """
            assert graphql(schema, query) == ({"node": {"id": "4", "width": 400}}, None)

        def gets_the_correct_typename_for_users():
            query = """
              {
                node(id: "1") {
                  id
                  __typename
                }
              }
            """
            assert graphql(schema, query) == (
                {"node": {"id": "1", "__typename": "User"}},
                None,
            )

        def gets_the_correct_typename_for_photos():
            query = """
              {
                node(id: "4") {
                  id
                  __typename
                }
              }
            """
            assert graphql(schema, query) == (
                {"node": {"id": "4", "__typename": "Photo"}},
                None,
            )

        def ignores_photo_fragments_on_user():
            query = """
              {
                node(id: "1") {
                  id
                  ... on Photo {
                    width
                  }
                }
              }
            """
            assert graphql(schema, query) == ({"node": {"id": "1"}}, None)

        def returns_null_for_bad_ids():
            query = """
              {
                node(id: "5") {
                  id
                }
              }
            """
            assert graphql(schema, query) == ({"node": None}, None)

        def returns_nulls_for_bad_ids():
            query = """
              {
                nodes(ids: ["3", "5"]) {
                  id
                }
              }
            """
            assert graphql(schema, query) == ({"nodes": [{"id": "3"}, None]}, None)

    def describe_introspection():
        def has_correct_node_interface():
            query = """
              {
                __type(name: "Node") {
                  name
                  kind
                  fields {
                    name
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
            """
            assert graphql(schema, query) == (
                {
                    "__type": {
                        "name": "Node",
                        "kind": "INTERFACE",
                        "fields": [
                            {
                                "name": "id",
                                "type": {
                                    "kind": "NON_NULL",
                                    "ofType": {"name": "ID", "kind": "SCALAR"},
                                },
                            }
                        ],
                    }
                },
                None,
            )

        def has_correct_node_and_nodes_root_field():
            query = """
              {
                __schema {
                  queryType {
                    fields {
                      name
                      type {
                        name
                        kind
                      }
                      args {
                        name
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
              }
            """
            assert graphql(schema, query) == (
                {
                    "__schema": {
                        "queryType": {
                            "fields": [
                                {
                                    "name": "node",
                                    "type": {"name": "Node", "kind": "INTERFACE"},
                                    "args": [
                                        {
                                            "name": "id",
                                            "type": {
                                                "kind": "NON_NULL",
                                                "ofType": {
                                                    "name": "ID",
                                                    "kind": "SCALAR",
                                                },
                                            },
                                        }
                                    ],
                                },
                                {
                                    "name": "nodes",
                                    "type": {"name": None, "kind": "NON_NULL"},
                                    "args": [
                                        {
                                            "name": "ids",
                                            "type": {
                                                "kind": "NON_NULL",
                                                "ofType": {
                                                    "name": None,
                                                    "kind": "LIST",
                                                },
                                            },
                                        }
                                    ],
                                },
                            ]
                        }
                    }
                },
                None,
            )


def describe_convert_global_ids():
    def to_global_id_converts_unicode_strings_correctly():
        my_unicode_id = "ûñö"
        g_id = to_global_id("MyType", my_unicode_id)
        assert g_id == "TXlUeXBlOsO7w7HDtg=="

        my_unicode_id = "\u06ED"
        g_id = to_global_id("MyType", my_unicode_id)
        assert g_id == "TXlUeXBlOtut"

    def from_global_id_converts_unicode_strings_correctly():
        my_unicode_id = "ûñö"
        my_type, my_id = from_global_id("TXlUeXBlOsO7w7HDtg==")
        assert my_type == "MyType"
        assert my_id == my_unicode_id

        my_unicode_id = "\u06ED"
        my_type, my_id = from_global_id("TXlUeXBlOtut")
        assert my_type == "MyType"
        assert my_id == my_unicode_id
