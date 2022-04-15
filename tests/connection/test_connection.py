from typing import List, NamedTuple

from graphql import (
    graphql_sync,
    print_schema,
    GraphQLField,
    GraphQLInt,
    GraphQLNonNull,
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

from ..utils import dedent


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
    GraphQLNonNull(user_type),
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
    GraphQLNonNull(user_type), resolve_node=lambda edge, _info: all_users[edge.node]
).connection_type


query_type = GraphQLObjectType(
    "Query",
    fields=lambda: {
        "user": GraphQLField(user_type, resolve=lambda _root, _info: all_users[0])
    },
)

schema = GraphQLSchema(query=query_type)


def describe_connection_definition():
    def includes_connection_and_edge_fields():
        source = """
            {
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
        assert graphql_sync(schema, source) == (
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

    def works_with_forward_connection_args():
        source = """
            {
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
        assert graphql_sync(schema, source) == (
            {
                "user": {
                    "friendsForward": {
                        "edges": [{"node": {"name": "Nick"}}, {"node": {"name": "Lee"}}]
                    }
                }
            },
            None,
        )

    def works_with_backward_connection_args():
        source = """
            {
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
        assert graphql_sync(schema, source) == (
            {
                "user": {
                    "friendsBackward": {
                        "edges": [{"node": {"name": "Joe"}}, {"node": {"name": "Tim"}}]
                    }
                }
            },
            None,
        )

    def generates_correct_types():
        assert print_schema(schema) == dedent(
            '''
            type Query {
              user: User
            }

            type User {
              name: String
              friends(
                """Returns the items in the list that come after the specified cursor."""
                after: String

                """Returns the first n items from the list."""
                first: Int

                """Returns the items in the list that come before the specified cursor."""
                before: String

                """Returns the last n items from the list."""
                last: Int
              ): FriendConnection
              friendsForward(
                """Returns the items in the list that come after the specified cursor."""
                after: String

                """Returns the first n items from the list."""
                first: Int
              ): UserConnection
              friendsBackward(
                """Returns the items in the list that come before the specified cursor."""
                before: String

                """Returns the last n items from the list."""
                last: Int
              ): UserConnection
            }

            """A connection to a list of items."""
            type FriendConnection {
              """Information to aid in pagination."""
              pageInfo: PageInfo!

              """A list of edges."""
              edges: [FriendEdge]
              totalCount: Int
            }

            """Information about pagination in a connection."""
            type PageInfo {
              """When paginating forwards, are there more items?"""
              hasNextPage: Boolean!

              """When paginating backwards, are there more items?"""
              hasPreviousPage: Boolean!

              """When paginating backwards, the cursor to continue."""
              startCursor: String

              """When paginating forwards, the cursor to continue."""
              endCursor: String
            }

            """An edge in a connection."""
            type FriendEdge {
              """The item at the end of the edge"""
              node: User!

              """A cursor for use in pagination"""
              cursor: String!
              friendshipTime: String
            }

            """A connection to a list of items."""
            type UserConnection {
              """Information to aid in pagination."""
              pageInfo: PageInfo!

              """A list of edges."""
              edges: [UserEdge]
            }

            """An edge in a connection."""
            type UserEdge {
              """The item at the end of the edge"""
              node: User!

              """A cursor for use in pagination"""
              cursor: String!
            }
            '''  # noqa: E501
        )
