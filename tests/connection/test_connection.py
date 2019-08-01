from typing import List, NamedTuple

from pytest import mark  # type: ignore

from graphql import graphql
from graphql.type import (
    GraphQLField,
    GraphQLInt,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
)

from graphql_relay import (
    backward_connection_args,
    connection_args,
    connection_definitions,
    connection_from_array,
    forward_connection_args,
)


class User(NamedTuple):
    name: str
    friends: List[int]


all_users = [
    User(name="Dan", friends=[1, 2, 3, 4]),
    User(name="Nick", friends=[0, 2, 3, 4]),
    User(name="Lee", friends=[0, 1, 3, 4]),
    User(name="Joe", friends=[0, 1, 2, 4]),
    User(name="Tim", friends=[0, 1, 2, 3]),
]

friend_connection: GraphQLObjectType
user_connection: GraphQLObjectType

user_type = GraphQLObjectType(
    "User",
    fields=lambda: {
        "name": GraphQLField(GraphQLString),
        "friends": GraphQLField(
            friend_connection,
            args=connection_args,
            resolve=lambda user, _info, **args: connection_from_array(
                user.friends, args
            ),
        ),
        "friendsForward": GraphQLField(
            user_connection,
            args=forward_connection_args,
            resolve=lambda user, _info, **args: connection_from_array(
                user.friends, args
            ),
        ),
        "friendsBackward": GraphQLField(
            user_connection,
            args=backward_connection_args,
            resolve=lambda user, _info, **args: connection_from_array(
                user.friends, args
            ),
        ),
    },
)

friend_connection = connection_definitions(
    user_type,
    name="Friend",
    resolve_node=lambda edge, _info: all_users[edge.node],
    edge_fields=lambda: {
        "friendshipTime": GraphQLField(
            GraphQLString, resolve=lambda user_, info_: "Yesterday"
        )
    },
    connection_fields=lambda: {
        "totalCount": GraphQLField(
            GraphQLInt, resolve=lambda _user, _info: len(all_users) - 1
        )
    },
).connection_type


user_connection = connection_definitions(
    user_type, resolve_node=lambda edge, _info: all_users[edge.node]
).connection_type


query_type = GraphQLObjectType(
    "Query",
    fields=lambda: {
        "user": GraphQLField(user_type, resolve=lambda _root, _info: all_users[0])
    },
)

schema = GraphQLSchema(query=query_type)


def describe_connection_definition():
    @mark.asyncio
    async def includes_connection_and_edge_fields():
        query = """
          query FriendsQuery {
            user {
              friends(first: 2) {
                totalCount
                edges {
                  friendshipTime
                  node {
                    name
                  }
                }
              }
            }
          }
        """
        assert await graphql(schema, query) == (
            {
                "user": {
                    "friends": {
                        "totalCount": 4,
                        "edges": [
                            {"friendshipTime": "Yesterday", "node": {"name": "Nick"}},
                            {"friendshipTime": "Yesterday", "node": {"name": "Lee"}},
                        ],
                    }
                }
            },
            None,
        )

    @mark.asyncio
    async def works_with_forward_connection_args():
        query = """
          query FriendsQuery {
            user {
              friendsForward(first: 2) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
          }
        """
        assert await graphql(schema, query) == (
            {
                "user": {
                    "friendsForward": {
                        "edges": [{"node": {"name": "Nick"}}, {"node": {"name": "Lee"}}]
                    }
                }
            },
            None,
        )

    @mark.asyncio
    async def works_with_backward_connection_args():
        query = """
          query FriendsQuery {
            user {
              friendsBackward(last: 2) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
          }
        """
        assert await graphql(schema, query) == (
            {
                "user": {
                    "friendsBackward": {
                        "edges": [{"node": {"name": "Joe"}}, {"node": {"name": "Tim"}}]
                    }
                }
            },
            None,
        )
