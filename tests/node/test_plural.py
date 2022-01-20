from typing import NamedTuple

from graphql import (
    graphql_sync,
    print_schema,
    GraphQLField,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLSchema,
    GraphQLString,
)

from graphql_relay import plural_identifying_root_field

from ..utils import dedent

user_type = GraphQLObjectType(
    "User",
    fields=lambda: {
        "username": GraphQLField(GraphQLString),
        "url": GraphQLField(GraphQLString),
    },
)


class User(NamedTuple):
    username: str
    url: str


def resolve_single_input(info: GraphQLResolveInfo, username: str) -> User:
    assert info.schema is schema
    lang = info.context.lang
    url = f"www.facebook.com/{username}?lang={lang}"
    return User(username=username, url=url)


query_type = GraphQLObjectType(
    "Query",
    lambda: {
        "usernames": plural_identifying_root_field(
            "usernames",
            description="Map from a username to the user",
            input_type=GraphQLString,
            output_type=user_type,
            resolve_single_input=resolve_single_input,
        )
    },
)

schema = GraphQLSchema(query=query_type)


class Context(NamedTuple):
    lang: str


def describe_plural_identifying_root_field():
    def allows_fetching():
        source = """
        {
          usernames(usernames:["dschafer", "leebyron", "schrockn"]) {
            username
            url
          }
        }
        """
        context_value = Context(lang="en")
        assert graphql_sync(schema, source, context_value=context_value) == (
            {
                "usernames": [
                    {
                        "username": "dschafer",
                        "url": "www.facebook.com/dschafer?lang=en",
                    },
                    {
                        "username": "leebyron",
                        "url": "www.facebook.com/leebyron?lang=en",
                    },
                    {
                        "username": "schrockn",
                        "url": "www.facebook.com/schrockn?lang=en",
                    },
                ]
            },
            None,
        )

    def generates_correct_types():
        assert print_schema(schema).rstrip == dedent(
            '''
            type Query {
              """Map from a username to the user"""
              usernames(usernames: [String!]!): [User]
            }

            type User {
              username: String
              url: String
            }
            '''
        )
