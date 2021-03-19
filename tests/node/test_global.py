from typing import Any, Dict, NamedTuple, Optional, Union

from pytest import fixture  # type: ignore

from graphql import graphql_sync as graphql
from graphql.type import (
    GraphQLField,
    GraphQLList,
    GraphQLInt,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLSchema,
    GraphQLString,
)

from graphql_relay import from_global_id, global_id_field, node_definitions


class User(NamedTuple):
    id: int
    name: str


class Photo(NamedTuple):
    photo_id: int
    width: int


class Post(NamedTuple):
    id: int
    text: str


@fixture(scope="module", params=["object_access", "dict_access"])
def schema(request):
    """Run each test with object access and dict access."""
    use_dicts = request.param == "dict_access"

    user_cls = dict if use_dicts else User
    user_data = {
        "1": user_cls(id=1, name="John Doe"),
        "2": user_cls(id=2, name="Jane Smith"),
    }

    photo_cls = dict if use_dicts else Photo
    photo_data = {
        "1": photo_cls(photo_id=1, width=300),
        "2": photo_cls(photo_id=2, width=400),
    }

    post_cls = dict if use_dicts else Post
    post_data = {"1": post_cls(id=1, text="lorem"), "2": post_cls(id=2, text="ipsum")}

    def get_node(
        global_id: str, info: GraphQLResolveInfo
    ) -> Optional[Union[User, Photo, Post, Dict]]:
        assert info.schema is schema
        type_, id_ = from_global_id(global_id)
        if type_ == "User":
            return user_data[id_]
        if type_ == "Photo":
            return photo_data[id_]
        if type_ == "Post":
            return post_data[id_]
        return None

    def get_node_type(
        obj: Union[User, Photo], info: GraphQLResolveInfo, _type: Any
    ) -> Optional[GraphQLObjectType]:
        assert info.schema is schema
        if "name" in obj if use_dicts else isinstance(obj, User):
            return user_type
        if "photo_id" in obj if use_dicts else isinstance(obj, Photo):
            return photo_type
        if "text" in obj if use_dicts else isinstance(obj, Post):
            return post_type
        return None

    node_interface, node_field = node_definitions(get_node, get_node_type)[:2]

    user_type = GraphQLObjectType(
        "User",
        fields=lambda: {
            "id": global_id_field("User"),
            "name": GraphQLField(GraphQLString),
        },
        interfaces=[node_interface],
    )

    photo_type = GraphQLObjectType(
        "Photo",
        fields=lambda: {
            "id": global_id_field(
                "Photo",
                lambda obj, _info: obj["photo_id"] if use_dicts else obj.photo_id,
            ),
            "width": GraphQLField(GraphQLInt),
        },
        interfaces=[node_interface],
    )

    post_type = GraphQLObjectType(
        "Post",
        fields=lambda: {"id": global_id_field(), "text": GraphQLField(GraphQLString)},
        interfaces=[node_interface],
    )

    query_type = GraphQLObjectType(
        "Query",
        fields=lambda: {
            "node": node_field,
            "allObjects": GraphQLField(
                GraphQLList(node_interface),
                resolve=lambda _root, _info: [
                    user_data["1"],
                    user_data["2"],
                    photo_data["1"],
                    photo_data["2"],
                    post_data["1"],
                    post_data["2"],
                ],
            ),
        },
    )

    schema = GraphQLSchema(query=query_type, types=[user_type, photo_type, post_type])

    yield schema


def describe_global_id_fields():
    def gives_different_ids(schema):
        query = """
        {
          allObjects {
            id
          }
        }
        """
        assert graphql(schema, query) == (
            {
                "allObjects": [
                    {"id": "VXNlcjox"},
                    {"id": "VXNlcjoy"},
                    {"id": "UGhvdG86MQ=="},
                    {"id": "UGhvdG86Mg=="},
                    {"id": "UG9zdDox"},
                    {"id": "UG9zdDoy"},
                ]
            },
            None,
        )

    def refetches_the_ids(schema):
        query = """
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
          post: node(id: "UG9zdDox") {
            id
            ... on Post {
              text
            }
          }
        }
        """
        assert graphql(schema, query) == (
            {
                "user": {"id": "VXNlcjox", "name": "John Doe"},
                "photo": {"id": "UGhvdG86MQ==", "width": 300},
                "post": {"id": "UG9zdDox", "text": "lorem"},
            },
            None,
        )
