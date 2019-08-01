from pytest import mark  # type: ignore

from graphql import graphql
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


simple_mutation = mutation_with_client_mutation_id(
    "SimpleMutation",
    input_fields={},
    output_fields={"result": GraphQLField(GraphQLInt)},
    mutate_and_get_payload=lambda _info, **_input: Result(1),
)

simple_mutation_with_description = mutation_with_client_mutation_id(
    "SimpleMutationWithDescription",
    description="Simple Mutation Description",
    input_fields={},
    output_fields={"result": GraphQLField(GraphQLInt)},
    mutate_and_get_payload=lambda _info, **_input: Result(1),
)

simple_mutation_with_deprecation_reason = mutation_with_client_mutation_id(
    "SimpleMutationWithDeprecationReason",
    input_fields={},
    output_fields={"result": GraphQLField(GraphQLInt)},
    mutate_and_get_payload=lambda _info, **_input: Result(1),
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
    @mark.asyncio
    async def requires_an_argument():
        query = """
          mutation M {
            simpleMutation {
              result
            }
          }
        """
        assert await graphql(schema, query) == (
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

    @mark.asyncio
    async def returns_the_same_client_mutation_id():
        query = """
          mutation M {
            simpleMutation(input: {clientMutationId: "abc"}) {
              result
              clientMutationId
            }
          }
        """
        assert await graphql(schema, query) == (
            {"simpleMutation": {"result": 1, "clientMutationId": "abc"}},
            None,
        )

    @mark.asyncio
    async def supports_thunks_as_input_and_output_fields():
        query = """
          mutation M {
            simpleMutationWithThunkFields(
                input: {inputData: 1234, clientMutationId: "abc"}) {
              result
              clientMutationId
            }
          }
        """
        assert await graphql(schema, query) == (
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
        query = """
          mutation M {
            simpleAsyncMutation(input: {clientMutationId: "abc"}) {
              result
              clientMutationId
            }
          }
        """
        assert await graphql(schema, query) == (
            {"simpleAsyncMutation": {"result": 1, "clientMutationId": "abc"}},
            None,
        )

    @mark.asyncio
    async def can_access_root_value():
        query = """
          mutation M {
            simpleRootValueMutation(input: {clientMutationId: "abc"}) {
              result
              clientMutationId
            }
          }
        """
        assert await graphql(schema, query, root_value=Result(1)) == (
            {"simpleRootValueMutation": {"result": 1, "clientMutationId": "abc"}},
            None,
        )

    def describe_introspection():
        @mark.asyncio
        async def contains_correct_input():
            query = """
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
            assert await graphql(schema, query) == (
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

        @mark.asyncio
        async def contains_correct_payload():
            query = """
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
            assert await graphql(schema, query) == (
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

        @mark.asyncio
        async def contains_correct_field():
            query = """
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
            assert await graphql(schema, query) == (
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

        @mark.asyncio
        async def contains_correct_descriptions():
            query = """
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
            assert await graphql(schema, query) == (
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

        @mark.asyncio
        async def contains_correct_deprecation_reason():
            query = """
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
            assert await graphql(schema, query) == (
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
