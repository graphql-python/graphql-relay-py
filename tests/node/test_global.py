from typing import Any, NamedTuple, Optional

from pytest import fixture

from graphql import (
    graphql_sync,
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
    id: str
    name: str


class Photo(NamedTuple):
    photo_id: str
    width: int


class Post(NamedTuple):
    id: str
    text: str


@fixture(scope="module", params=["object_access", "dict_access"])
def schema(request):
    """Run each test with object access and dict access."""
    use_dicts = request.param == "dict_access"

    user_cls = dict if use_dicts else User
    user_data = [
        user_cls(id="1", name="John Doe"),
        user_cls(id="2", name="Jane Smith"),
    ]

    photo_cls = dict if use_dicts else Photo
    photo_data = [
        photo_cls(photo_id="1", width=300),
        photo_cls(photo_id="2", width=400),
    ]

    post_cls = dict if use_dicts else Post
    post_data = [post_cls(id="1", text="lorem"), post_cls(id="2", text="ipsum")]

    if use_dicts:

        def get_node(global_id: str, info: GraphQLResolveInfo) -> Any:
            assert info.schema is schema
            type_, id_ = from_global_id(global_id)
            if type_ == "User":
                return next(filter(lambda obj: obj["id"] == id_, user_data), None)
            if type_ == "Photo":
                return next(
                    filter(lambda obj: obj["photo_id"] == id_, photo_data), None
                )
            if type_ == "Post":
                return next(filter(lambda obj: obj["id"] == id_, post_data), None)
            return None  # pragma: no cover

        def get_node_type(
            obj: Any, info: GraphQLResolveInfo, _type: Any
        ) -> Optional[GraphQLObjectType]:
            assert info.schema is schema
            if "name" in obj:
                return user_type
            if "photo_id" in obj:
                return photo_type
            if "text" in obj:
                return post_type
            return None  # pragma: no cover

    else:

        def get_node(global_id: str, info: GraphQLResolveInfo) -> Any:
            assert info.schema is schema
            type_, id_ = from_global_id(global_id)
            if type_ == "User":
                return next(filter(lambda obj: obj.id == id_, user_data), None)
            if type_ == "Photo":
                return next(filter(lambda obj: obj.photo_id == id_, photo_data), None)
            if type_ == "Post":
                return next(filter(lambda obj: obj.id == id_, post_data), None)
            return None  # pragma: no cover

        def get_node_type(
            obj: Any, info: GraphQLResolveInfo, _type: Any
        ) -> Optional[GraphQLObjectType]:
            assert info.schema is schema
            if isinstance(obj, User):
                return user_type
            if isinstance(obj, Photo):
                return photo_type
            if isinstance(obj, Post):
                return post_type
            return None  # pragma: no cover

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
                resolve=lambda _root, _info: [*user_data, *photo_data, *post_data],
            ),
        },
    )

    schema = GraphQLSchema(query=query_type, types=[user_type, photo_type, post_type])

    yield schema


def describe_global_id_fields():
    def gives_different_ids(schema):
        source = """
        {
          allObjects {
            id
          }
        }
        """
        assert graphql_sync(schema, source) == (
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

    def allows_to_refetch_the_ids(schema):
        source = """
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
        assert graphql_sync(schema, source) == (
            {
                "user": {"id": "VXNlcjox", "name": "John Doe"},
                "photo": {"id": "UGhvdG86MQ==", "width": 300},
                "post": {"id": "UG9zdDox", "text": "lorem"},
            },
            None,
        )

    def handles_valid_global_ids():
        assert from_global_id("Zm9v") == ("", "foo")
        assert from_global_id(b"Zm9v") == ("", "foo")  # type: ignore
        assert from_global_id("Zm9vOmJhcg==") == ("foo", "bar")
        assert from_global_id(b"Zm9vOmJhcg==") == ("foo", "bar")  # type: ignore

    def handles_invalid_global_ids():
        assert from_global_id("") == ("", "")
        assert from_global_id("Og==") == ("", "")
        assert from_global_id("bad!") == ("", "")
        assert from_global_id("invalid") == ("", "")
