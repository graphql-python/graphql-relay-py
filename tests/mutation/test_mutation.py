from pytest import mark  # type: ignore

from graphql import graphql, graphql_sync
from graphql.type import (
    GraphQLField,
    GraphQLInputField,
    GraphQLInt,
    GraphQLObjectType,
    GraphQLSchema,
)

from graphql_relay import mutation_with_client_mutation_id


class Result:

    # noinspection PyPep8Naming
    def __init__(self, result, clientMutationId=None):
        self.clientMutationId = clientMutationId
        self.result = result


def dummy_resolve(_info, **_input):
    return Result(1)


simple_mutation = mutation_with_client_mutation_id(
    "SimpleMutation",
    input_fields={},
    output_fields={"result": GraphQLField(GraphQLInt)},
    mutate_and_get_payload=dummy_resolve,
)

simple_mutation_with_description = mutation_with_client_mutation_id(
    "SimpleMutationWithDescription",
    description="Simple Mutation Description",
    input_fields={},
    output_fields={"result": GraphQLField(GraphQLInt)},
    mutate_and_get_payload=dummy_resolve,
)

simple_mutation_with_deprecation_reason = mutation_with_client_mutation_id(
    "SimpleMutationWithDeprecationReason",
    input_fields={},
    output_fields={"result": GraphQLField(GraphQLInt)},
    mutate_and_get_payload=dummy_resolve,
    deprecation_reason="Just because",
)

# noinspection PyPep8Naming
simple_mutation_with_thunk_fields = mutation_with_client_mutation_id(
    "SimpleMutationWithThunkFields",
    input_fields=lambda: {"inputData": GraphQLInputField(GraphQLInt)},
    output_fields=lambda: {"result": GraphQLField(GraphQLInt)},
    mutate_and_get_payload=lambda _info, inputData, **_input: Result(inputData),
)


# noinspection PyPep8Naming
async def mutate_and_get_one_as_payload_async(_info, **_input):
    return Result(1)


simple_async_mutation = mutation_with_client_mutation_id(
    "SimpleAsyncMutation",
    input_fields={},
    output_fields={"result": GraphQLField(GraphQLInt)},
    mutate_and_get_payload=mutate_and_get_one_as_payload_async,
)

simple_root_value_mutation = mutation_with_client_mutation_id(
    "SimpleRootValueMutation",
    input_fields={},
    output_fields={"result": GraphQLField(GraphQLInt)},
    mutate_and_get_payload=lambda info, **_input: info.root_value,
)

query_type: GraphQLObjectType = GraphQLObjectType(
    "Query", lambda: {"query": GraphQLField(query_type)}
)

mutation_type = GraphQLObjectType(
    "Mutation",
    fields={
        "simpleMutation": simple_mutation,
        "simpleMutationWithDescription": simple_mutation_with_description,
        "simpleMutationWithDeprecationReason": simple_mutation_with_deprecation_reason,
        "simpleMutationWithThunkFields": simple_mutation_with_thunk_fields,
        "simpleAsyncMutation": simple_async_mutation,
        "simpleRootValueMutation": simple_root_value_mutation,
    },
)

schema = GraphQLSchema(query=query_type, mutation=mutation_type)


def describe_mutation_with_client_mutation_id():
    def requires_an_argument():
        source = """
          mutation M {
            simpleMutation {
              result
            }
          }
        """
        assert graphql_sync(schema, source) == (
            None,
            [
                {
                    "message": "Field 'simpleMutation' argument 'input'"
                    " of type 'SimpleMutationInput!' is required,"
                    " but it was not provided.",
                    "locations": [(3, 13)],
                }
            ],
        )

    def returns_the_same_client_mutation_id():
        source = """
          mutation M {
            simpleMutation(input: {clientMutationId: "abc"}) {
              result
              clientMutationId
            }
          }
        """
        assert graphql_sync(schema, source) == (
            {"simpleMutation": {"result": 1, "clientMutationId": "abc"}},
            None,
        )

    def supports_thunks_as_input_and_output_fields():
        source = """
          mutation M {
            simpleMutationWithThunkFields(
                input: {inputData: 1234, clientMutationId: "abc"}) {
              result
              clientMutationId
            }
          }
        """
        assert graphql_sync(schema, source) == (
            {
                "simpleMutationWithThunkFields": {
                    "result": 1234,
                    "clientMutationId": "abc",
                }
            },
            None,
        )

    @mark.asyncio
    async def supports_async_mutations():
        source = """
          mutation M {
            simpleAsyncMutation(input: {clientMutationId: "abc"}) {
              result
              clientMutationId
            }
          }
        """
        assert await graphql(schema, source) == (
            {"simpleAsyncMutation": {"result": 1, "clientMutationId": "abc"}},
            None,
        )

    def can_access_root_value():
        source = """
          mutation M {
            simpleRootValueMutation(input: {clientMutationId: "abc"}) {
              result
              clientMutationId
            }
          }
        """
        assert graphql_sync(schema, source, root_value=Result(1)) == (
            {"simpleRootValueMutation": {"result": 1, "clientMutationId": "abc"}},
            None,
        )

    def supports_mutations_returning_null():
        source = """
          mutation M {
            simpleRootValueMutation(input: {clientMutationId: "abc"}) {
              result
              clientMutationId
            }
          }
        """
        assert graphql_sync(schema, source, root_value=None) == (
            {"simpleRootValueMutation": {"result": None, "clientMutationId": "abc"}},
            None,
        )

    def describe_introspection():
        def contains_correct_input():
            source = """
              {
                __type(name: "SimpleMutationInput") {
                  name
                  kind
                  inputFields {
                    name
                    type {
                      name
                      kind
                    }
                  }
                }
              }
            """
            assert graphql_sync(schema, source) == (
                {
                    "__type": {
                        "name": "SimpleMutationInput",
                        "kind": "INPUT_OBJECT",
                        "inputFields": [
                            {
                                "name": "clientMutationId",
                                "type": {"name": None, "kind": "NON_NULL"},
                            }
                        ],
                    }
                },
                None,
            )

        def contains_correct_payload():
            source = """
              {
                __type(name: "SimpleMutationPayload") {
                  name
                  kind
                  fields {
                    name
                    type {
                      name
                      kind
                    }
                  }
                }
              }
            """
            assert graphql_sync(schema, source) == (
                {
                    "__type": {
                        "name": "SimpleMutationPayload",
                        "kind": "OBJECT",
                        "fields": [
                            {
                                "name": "result",
                                "type": {"name": "Int", "kind": "SCALAR"},
                            },
                            {
                                "name": "clientMutationId",
                                "type": {"name": None, "kind": "NON_NULL"},
                            },
                        ],
                    }
                },
                None,
            )

        def contains_correct_field():
            source = """
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
            """
            assert graphql_sync(schema, source) == (
                {
                    "__schema": {
                        "mutationType": {
                            "fields": [
                                {
                                    "name": "simpleMutation",
                                    "args": [
                                        {
                                            "name": "input",
                                            "type": {
                                                "name": None,
                                                "kind": "NON_NULL",
                                                "ofType": {
                                                    "name": "SimpleMutationInput",
                                                    "kind": "INPUT_OBJECT",
                                                },
                                            },
                                        }
                                    ],
                                    "type": {
                                        "name": "SimpleMutationPayload",
                                        "kind": "OBJECT",
                                    },
                                },
                                {
                                    "name": "simpleMutationWithDescription",
                                    "args": [
                                        {
                                            "name": "input",
                                            "type": {
                                                "name": None,
                                                "kind": "NON_NULL",
                                                "ofType": {
                                                    "name": "SimpleMutation"
                                                    "WithDescriptionInput",
                                                    "kind": "INPUT_OBJECT",
                                                },
                                            },
                                        }
                                    ],
                                    "type": {
                                        "name": "SimpleMutationWithDescriptionPayload",
                                        "kind": "OBJECT",
                                    },
                                },
                                {
                                    "name": "simpleMutationWithThunkFields",
                                    "args": [
                                        {
                                            "name": "input",
                                            "type": {
                                                "name": None,
                                                "kind": "NON_NULL",
                                                "ofType": {
                                                    "name": "SimpleMutation"
                                                    "WithThunkFieldsInput",
                                                    "kind": "INPUT_OBJECT",
                                                },
                                            },
                                        }
                                    ],
                                    "type": {
                                        "name": "SimpleMutationWithThunkFieldsPayload",
                                        "kind": "OBJECT",
                                    },
                                },
                                {
                                    "name": "simpleAsyncMutation",
                                    "args": [
                                        {
                                            "name": "input",
                                            "type": {
                                                "name": None,
                                                "kind": "NON_NULL",
                                                "ofType": {
                                                    "name": "SimpleAsyncMutationInput",
                                                    "kind": "INPUT_OBJECT",
                                                },
                                            },
                                        }
                                    ],
                                    "type": {
                                        "name": "SimpleAsyncMutationPayload",
                                        "kind": "OBJECT",
                                    },
                                },
                                {
                                    "name": "simpleRootValueMutation",
                                    "args": [
                                        {
                                            "name": "input",
                                            "type": {
                                                "name": None,
                                                "kind": "NON_NULL",
                                                "ofType": {
                                                    "name": "SimpleRootValueMutationInput",  # noqa: E501
                                                    "kind": "INPUT_OBJECT",
                                                },
                                            },
                                        }
                                    ],
                                    "type": {
                                        "name": "SimpleRootValueMutationPayload",
                                        "kind": "OBJECT",
                                    },
                                },
                            ]
                        }
                    }
                },
                None,
            )

        def contains_correct_descriptions():
            source = """
              {
                __schema {
                  mutationType {
                    fields {
                      name
                      description
                    }
                  }
                }
              }
            """
            assert graphql_sync(schema, source) == (
                {
                    "__schema": {
                        "mutationType": {
                            "fields": [
                                {"name": "simpleMutation", "description": None},
                                {
                                    "name": "simpleMutationWithDescription",
                                    "description": "Simple Mutation Description",
                                },
                                {
                                    "name": "simpleMutationWithThunkFields",
                                    "description": None,
                                },
                                {"name": "simpleAsyncMutation", "description": None},
                                {
                                    "name": "simpleRootValueMutation",
                                    "description": None,
                                },
                            ]
                        }
                    }
                },
                None,
            )

        def contains_correct_deprecation_reason():
            source = """
              {
                __schema {
                  mutationType {
                    fields(includeDeprecated: true) {
                      name
                      isDeprecated
                      deprecationReason
                    }
                  }
                }
              }
            """
            assert graphql_sync(schema, source) == (
                {
                    "__schema": {
                        "mutationType": {
                            "fields": [
                                {
                                    "name": "simpleMutation",
                                    "isDeprecated": False,
                                    "deprecationReason": None,
                                },
                                {
                                    "name": "simpleMutationWithDescription",
                                    "isDeprecated": False,
                                    "deprecationReason": None,
                                },
                                {
                                    "name": "simpleMutationWithDeprecationReason",
                                    "isDeprecated": True,
                                    "deprecationReason": "Just because",
                                },
                                {
                                    "name": "simpleMutationWithThunkFields",
                                    "isDeprecated": False,
                                    "deprecationReason": None,
                                },
                                {
                                    "name": "simpleAsyncMutation",
                                    "isDeprecated": False,
                                    "deprecationReason": None,
                                },
                                {
                                    "name": "simpleRootValueMutation",
                                    "isDeprecated": False,
                                    "deprecationReason": None,
                                },
                            ]
                        }
                    }
                },
                None,
            )
