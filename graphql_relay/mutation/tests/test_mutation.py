from promise import Promise

from graphql import graphql
from graphql.type import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLInt,
    GraphQLField,
    GraphQLInputObjectField
)

from ..mutation import mutation_with_client_mutation_id


class Result(object):

    def __init__(self, result, clientMutationId=None):
        self.clientMutationId = clientMutationId
        self.result = result


simpleMutation = mutation_with_client_mutation_id(
    'SimpleMutation',
    input_fields={},
    output_fields={
        'result': GraphQLField(GraphQLInt)
    },
    mutate_and_get_payload=lambda _info, **_input: Result(result=1)
)

simpleMutationWithThunkFields = mutation_with_client_mutation_id(
    'SimpleMutationWithThunkFields',
    input_fields=lambda: {
        'inputData': GraphQLInputObjectField(GraphQLInt)
    },
    output_fields=lambda: {
        'result': GraphQLField(GraphQLInt)
    },
    mutate_and_get_payload=lambda _info, **input_: Result(result=input_['inputData'])
)

simplePromiseMutation = mutation_with_client_mutation_id(
    'SimplePromiseMutation',
    input_fields={},
    output_fields={
        'result': GraphQLField(GraphQLInt)
    },
    mutate_and_get_payload=lambda _info, **_input: Promise.resolve(Result(result=1))
)

simpleRootValueMutation = mutation_with_client_mutation_id(
    'SimpleRootValueMutation',
    input_fields={},
    output_fields={
        'result': GraphQLField(GraphQLInt)
    },
    mutate_and_get_payload=lambda info, **_input: info.root_value
)

mutation = GraphQLObjectType(
    'Mutation',
    fields={
        'simpleMutation': simpleMutation,
        'simpleMutationWithThunkFields': simpleMutationWithThunkFields,
        'simplePromiseMutation': simplePromiseMutation,
        'simpleRootValueMutation': simpleRootValueMutation
    }
)

schema = GraphQLSchema(
    query=mutation,
    mutation=mutation
)


def test_requires_an_argument():
    query = '''
      mutation M {
        simpleMutation {
          result
        }
      }
    '''
    result = graphql(schema, query)
    assert len(result.errors) == 1


def test_returns_the_same_client_mutation_id():
    query = '''
      mutation M {
        simpleMutation(input: {clientMutationId: "abc"}) {
          result
          clientMutationId
        }
      }
    '''
    expected = {
        'simpleMutation': {
            'result': 1,
            'clientMutationId': 'abc'
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_supports_thunks_as_input_and_output_fields():
    query = '''
      mutation M {
        simpleMutationWithThunkFields(
            input: {inputData: 1234, clientMutationId: "abc"}) {
          result
          clientMutationId
        }
      }
    '''
    expected = {
        'simpleMutationWithThunkFields': {
            'result': 1234,
            'clientMutationId': 'abc'
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_supports_promise_mutations():
    query = '''
      mutation M {
        simplePromiseMutation(input: {clientMutationId: "abc"}) {
          result
          clientMutationId
        }
      }
    '''
    expected = {
        'simplePromiseMutation': {
            'result': 1,
            'clientMutationId': 'abc'
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_can_access_root_value():
    query = '''
      mutation M {
        simpleRootValueMutation(input: {clientMutationId: "abc"}) {
          result
          clientMutationId
        }
      }
    '''
    expected = {
        'simpleRootValueMutation': {
            'result': 1,
            'clientMutationId': 'abc'
        }
    }
    result = graphql(schema, query, root=Result(result=1))
    assert not result.errors
    assert result.data == expected


def test_contains_correct_input():
    query = '''
      {
        __type(name: "SimpleMutationInput") {
          name
          kind
          inputFields {
            name
            type {
              name
              kind
              ofType {
                name
                kind
              }
            }
          }
        }
      }
    '''
    expected = {
        '__type': {
            'name': 'SimpleMutationInput',
            'kind': 'INPUT_OBJECT',
            'inputFields': [
                {
                    'name': 'clientMutationId',
                    'type': {
                        'name': None,
                        'kind': 'NON_NULL',
                        'ofType': {
                            'name': 'String',
                            'kind': 'SCALAR'
                        }
                    }
                }
            ]
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_contains_correct_payload():
    query = '''
      {
        __type(name: "SimpleMutationPayload") {
          name
          kind
          fields {
            name
            type {
              name
              kind
              ofType {
                name
                kind
              }
            }
          }
        }
      }
    '''
    expected1 = {
        '__type': {
            'name': 'SimpleMutationPayload',
            'kind': 'OBJECT',
            'fields': [
                {
                    'name': 'clientMutationId',
                    'type': {
                        'name': None,
                        'kind': 'NON_NULL',
                        'ofType': {
                            'name': 'String',
                            'kind': 'SCALAR'
                        }
                    }
                },
                {
                    'name': 'result',
                    'type': {
                        'name': 'Int',
                        'kind': 'SCALAR',
                        'ofType': None
                    }
                },
            ]
        }
    }
    expected2 = {
        '__type': {
            'name': 'SimpleMutationPayload',
            'kind': 'OBJECT',
            'fields': [
                {
                    'name': 'result',
                    'type': {
                        'name': 'Int',
                        'kind': 'SCALAR',
                        'ofType': None
                    }
                },
                {
                    'name': 'clientMutationId',
                    'type': {
                        'name': None,
                        'kind': 'NON_NULL',
                        'ofType': {
                            'name': 'String',
                            'kind': 'SCALAR'
                        }
                    }
                },
            ]
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected1 or result.data == expected2


def test_contains_correct_field():
    query = '''
      {
        __schema {
          mutationType {
            fields {
              name
              args {
                name
                type {
                  name
                  kind
                  ofType {
                    name
                    kind
                  }
                }
              }
              type {
                name
                kind
              }
            }
          }
        }
      }
    '''
    expected = {
        '__schema': {
            'mutationType': {
                'fields': [
                    {
                        'name': 'simplePromiseMutation',
                        'args': [
                            {
                                'name': 'input',
                                'type': {
                                    'name': None,
                                    'kind': 'NON_NULL',
                                    'ofType': {
                                        'name': 'SimplePromiseMutationInput',
                                        'kind': 'INPUT_OBJECT'
                                    }
                                },
                            }
                        ],
                        'type': {
                            'name': 'SimplePromiseMutationPayload',
                            'kind': 'OBJECT',
                        }
                    },
                    {
                        'name': 'simpleRootValueMutation',
                        'args': [
                            {
                                'name': 'input',
                                'type': {
                                    'name': None,
                                    'kind': 'NON_NULL',
                                    'ofType': {
                                        'name': 'SimpleRootValueMutationInput',
                                        'kind': 'INPUT_OBJECT'
                                    }
                                },
                            }
                        ],
                        'type': {
                            'name': 'SimpleRootValueMutationPayload',
                            'kind': 'OBJECT',
                        }
                    },
                    {
                        'name': 'simpleMutation',
                        'args': [
                            {
                                'name': 'input',
                                'type': {
                                    'name': None,
                                    'kind': 'NON_NULL',
                                    'ofType': {
                                        'name': 'SimpleMutationInput',
                                        'kind': 'INPUT_OBJECT'
                                    }
                                },
                            }
                        ],
                        'type': {
                            'name': 'SimpleMutationPayload',
                            'kind': 'OBJECT',
                        }
                    },
                    {
                        'name': 'simpleMutationWithThunkFields',
                        'args': [
                            {
                                'name': 'input',
                                'type': {
                                    'name': None,
                                    'kind': 'NON_NULL',
                                    'ofType': {
                                        'name': 'SimpleMutationWithThunkFieldsInput',
                                        'kind': 'INPUT_OBJECT'
                                    }
                                },
                            }
                        ],
                        'type': {
                            'name': 'SimpleMutationWithThunkFieldsPayload',
                            'kind': 'OBJECT',
                        }
                    },
                ]
            }
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    # ensure the ordering is correct for the assertion
    expected['__schema']['mutationType']['fields'] = sorted(
        expected['__schema']['mutationType']['fields'],
        key=lambda k: k['name']
    )
    result.data['__schema']['mutationType']['fields'] = sorted(
        result.data['__schema']['mutationType']['fields'],
        key=lambda k: k['name']
    )
    assert result.data == expected
