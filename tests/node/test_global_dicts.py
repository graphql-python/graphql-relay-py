from typing import Any, Dict

from graphql import graphql_sync as graphql
from graphql.type import (
    GraphQLField,
    GraphQLList,
    GraphQLInt,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLSchema,
    GraphQLString)

from graphql_relay import from_global_id, global_id_field, node_definitions


user_data = {
    '1': dict(id=1, name='John Doe'),
    '2': dict(id=2, name='Jane Smith'),
}

photo_data = {
    '1': dict(photo_id=1, width=300),
    '2': dict(photo_id=2, width=400),
}

post_data = {
    '1': dict(id=1, text='lorem'),
    '2': dict(id=2, text='ipsum')
}


def get_node(global_id: str, info: GraphQLResolveInfo) -> Dict[str, Any]:
    assert info.schema is schema
    type_, id_ = from_global_id(global_id)
    if type_ == 'User':
        return user_data[id_]
    if type_ == 'Photo':
        return photo_data[id_]
    if type_ == 'Post':
        return post_data[id_]


def get_node_type(
        obj: Dict[str, Any], info: GraphQLResolveInfo,
        _type: Any) -> GraphQLObjectType:
    assert info.schema is schema
    if 'name' in obj:
        return user_type
    if 'photo_id' in obj:
        return photo_type
    if 'text' in obj:
        return post_type


node_interface, node_field = node_definitions(get_node, get_node_type)[:2]

user_type = GraphQLObjectType(
    'User',
    fields=lambda: {
        'id': global_id_field('User'),
        'name': GraphQLField(GraphQLString),
    },
    interfaces=[node_interface]
)

photo_type = GraphQLObjectType(
    'Photo',
    fields=lambda: {
        'id': global_id_field('Photo', lambda obj, _info: obj['photo_id']),
        'width': GraphQLField(GraphQLInt),
    },
    interfaces=[node_interface]
)

post_type = GraphQLObjectType(
    'Post',
    fields=lambda: {
        'id': global_id_field(),
        'text': GraphQLField(GraphQLString),
    },
    interfaces=[node_interface]
)

query_type = GraphQLObjectType(
    'Query',
    fields=lambda: {
        'node': node_field,
        'allObjects': GraphQLField(
            GraphQLList(node_interface),
            resolve=lambda _root, _info: [
                user_data['1'], user_data['2'],
                photo_data['1'], photo_data['2'],
                post_data['1'], post_data['2']
            ]
        )
    }
)

schema = GraphQLSchema(
    query=query_type,
    types=[user_type, photo_type, post_type]
)


def describe_global_id_fields():

    def gives_different_ids():
        query = '''
        {
          allObjects {
            id
          }
        }
        '''
        assert graphql(schema, query) == (
            {
                'allObjects': [
                    {
                        'id': 'VXNlcjox'
                    },
                    {
                        'id': 'VXNlcjoy'
                    },
                    {
                        'id': 'UGhvdG86MQ=='
                    },
                    {
                        'id': 'UGhvdG86Mg=='
                    },
                    {
                        'id': 'UG9zdDox',
                    },
                    {
                        'id': 'UG9zdDoy',
                    },
                ]
            },
            None
        )

    def refetches_the_ids():
        query = '''
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
        '''
        assert graphql(schema, query) == (
            {
                'user': {
                    'id': 'VXNlcjox',
                    'name': 'John Doe'
                },
                'photo': {
                    'id': 'UGhvdG86MQ==',
                    'width': 300
                },
                'post': {
                    'id': 'UG9zdDox',
                    'text': 'lorem',
                },
            },
            None
        )
