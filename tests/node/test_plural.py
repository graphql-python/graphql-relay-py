from typing import NamedTuple

from graphql import graphql_sync
from graphql.type import (
    GraphQLField,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLSchema,
    GraphQLString,
)

from graphql_relay import plural_identifying_root_field

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


class Context:
    lang = "en"


def describe_plural_identifying_root_field():
    def allows_fetching():
        query = """
        {
          usernames(usernames:["dschafer", "leebyron", "schrockn"]) {
            username
            url
          }
        }
        """
        assert graphql_sync(schema, query, context_value=Context()) == (
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

    def correctly_introspects():
        query = """
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
        """
        assert graphql_sync(schema, query) == (
            {
                "__schema": {
                    "queryType": {
                        "fields": [
                            {
                                "name": "usernames",
                                "args": [
                                    {
                                        "name": "usernames",
                                        "type": {
                                            "kind": "NON_NULL",
                                            "ofType": {
                                                "kind": "LIST",
                                                "ofType": {
                                                    "kind": "NON_NULL",
                                                    "ofType": {
                                                        "name": "String",
                                                        "kind": "SCALAR",
                                                    },
                                                },
                                            },
                                        },
                                    }
                                ],
                                "type": {
                                    "kind": "LIST",
                                    "ofType": {"name": "User", "kind": "OBJECT"},
                                },
                            }
                        ]
                    }
                }
            },
            None,
        )
