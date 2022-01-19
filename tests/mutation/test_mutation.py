from pytest import mark

from graphql import graphql, graphql_sync
from graphql.type import (
    GraphQLField,
    GraphQLFieldMap,
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


def dummy_resolve(_info, inputData=None, clientMutationId=None):
    return Result(inputData or 1, clientMutationId)


async def dummy_resolve_async(_info, inputData=None, clientMutationId=None):
    return Result(inputData or 1, clientMutationId)


def wrap_in_schema(mutation_fields: GraphQLFieldMap) -> GraphQLSchema:
    query_type = GraphQLObjectType(
        "DummyQuery", fields={"dummy": GraphQLField(GraphQLInt)}
    )
    mutation_type = GraphQLObjectType("Mutation", fields=mutation_fields)
    return GraphQLSchema(query_type, mutation_type)


def describe_mutation_with_client_mutation_id():
    def requires_an_argument():
        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation", {}, {"result": GraphQLField(GraphQLInt)}, dummy_resolve
        )
        schema = wrap_in_schema({"someMutation": some_mutation})
        source = """
            mutation {
              someMutation {
                result
              }
            }
            """
        assert graphql_sync(schema, source) == (
            None,
            [
                {
                    "message": "Field 'someMutation' argument 'input'"
                    " of type 'SomeMutationInput!' is required,"
                    " but it was not provided.",
                    "locations": [(3, 15)],
                }
            ],
        )

    def returns_the_same_client_mutation_id():
        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation", {}, {"result": GraphQLField(GraphQLInt)}, dummy_resolve
        )
        schema = wrap_in_schema({"someMutation": some_mutation})
        source = """
            mutation {
              someMutation(input: {clientMutationId: "abc"}) {
                result
                clientMutationId
              }
            }
            """
        assert graphql_sync(schema, source) == (
            {"someMutation": {"result": 1, "clientMutationId": "abc"}},
            None,
        )

    def supports_thunks_as_input_and_output_fields():
        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation",
            {"inputData": GraphQLInputField(GraphQLInt)},
            {"result": GraphQLField(GraphQLInt)},
            dummy_resolve,
        )
        schema = wrap_in_schema({"someMutation": some_mutation})
        source = """
            mutation {
              someMutation(input: {inputData: 1234, clientMutationId: "abc"}) {
                result
                clientMutationId
              }
            }
            """
        assert graphql_sync(schema, source) == (
            {
                "someMutation": {
                    "result": 1234,
                    "clientMutationId": "abc",
                }
            },
            None,
        )

    @mark.asyncio
    async def supports_async_mutations():
        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation",
            {},
            {"result": GraphQLField(GraphQLInt)},
            dummy_resolve_async,
        )
        schema = wrap_in_schema({"someMutation": some_mutation})
        source = """
            mutation {
              someMutation(input: {clientMutationId: "abc"}) {
                result
                clientMutationId
              }
            }
            """
        assert await graphql(schema, source) == (
            {"someMutation": {"result": 1, "clientMutationId": "abc"}},
            None,
        )

    def can_access_root_value():
        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation",
            {},
            {"result": GraphQLField(GraphQLInt)},
            lambda info, clientMutationId=None: Result(
                info.root_value, clientMutationId
            ),
        )
        schema = wrap_in_schema({"someMutation": some_mutation})
        source = """
            mutation {
              someMutation(input: {clientMutationId: "abc"}) {
                result
                clientMutationId
              }
            }
            """
        assert graphql_sync(schema, source, root_value=1) == (
            {"someMutation": {"result": 1, "clientMutationId": "abc"}},
            None,
        )

    def supports_mutations_returning_null():
        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation",
            {},
            {"result": GraphQLField(GraphQLInt)},
            lambda _info, **_input: None,
        )
        schema = wrap_in_schema({"someMutation": some_mutation})
        source = """
            mutation {
              someMutation(input: {clientMutationId: "abc"}) {
                result
                clientMutationId
              }
            }
            """
        assert graphql_sync(schema, source) == (
            {"someMutation": {"result": None, "clientMutationId": "abc"}},
            None,
        )

    def describe_introspection():
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

        schema = wrap_in_schema(
            {
                "simpleMutation": simple_mutation,
                "simpleMutationWithDescription": simple_mutation_with_description,
                "simpleMutationWithDeprecationReason": simple_mutation_with_deprecation_reason,  # noqa: E501
            }
        )

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
                            ]
                        }
                    }
                },
                None,
            )
