from pytest import mark

from graphql import (
    graphql,
    graphql_sync,
    print_schema,
    GraphQLField,
    GraphQLFieldMap,
    GraphQLInputField,
    GraphQLInt,
    GraphQLObjectType,
    GraphQLSchema,
)

from graphql_relay import mutation_with_client_mutation_id

from ..utils import dedent


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
    query_type = GraphQLObjectType("Query", fields={"dummy": GraphQLField(GraphQLInt)})
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
        def null_resolve(_info, **_input):
            return None

        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation", {}, {"result": GraphQLField(GraphQLInt)}, null_resolve
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

    @mark.asyncio
    async def supports_async_mutations_returning_null():
        async def null_resolve(_info, **_input):
            return None

        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation",
            {},
            {"result": GraphQLField(GraphQLInt)},
            null_resolve,
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
            {"someMutation": {"result": None, "clientMutationId": "abc"}},
            None,
        )

    def supports_mutations_returning_custom_classes():
        class SomeClass:
            @staticmethod
            def get_some_generated_data():
                return 1

            @classmethod
            def mutate(cls, _info, **_input):
                return cls()

            @classmethod
            def resolve(cls, obj, _info):
                assert isinstance(obj, cls)
                return obj.get_some_generated_data()

        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation",
            {},
            {"result": GraphQLField(GraphQLInt, resolve=SomeClass.resolve)},
            SomeClass.mutate,
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

    def supports_mutations_returning_mappings():
        def dict_mutate(_info, **_input):
            return {"some_data": 1}

        def dict_resolve(obj, _info):
            return obj["some_data"]

        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation",
            {},
            {"result": GraphQLField(GraphQLInt, resolve=dict_resolve)},
            dict_mutate,
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

    @mark.asyncio
    async def supports_async_mutations_returning_mappings():
        async def dict_mutate(_info, **_input):
            return {"some_data": 1}

        async def dict_resolve(obj, _info):
            return obj["some_data"]

        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation",
            {},
            {"result": GraphQLField(GraphQLInt, resolve=dict_resolve)},
            dict_mutate,
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

    def generates_correct_types():
        some_mutation = mutation_with_client_mutation_id(
            "SomeMutation",
            description="Some Mutation Description",
            input_fields={},
            output_fields={"result": GraphQLField(GraphQLInt)},
            mutate_and_get_payload=dummy_resolve,
            deprecation_reason="Just because",
        )

        schema = wrap_in_schema({"someMutation": some_mutation})

        assert print_schema(schema).rstrip() == dedent(
            '''
            type Query {
              dummy: Int
            }

            type Mutation {
              """Some Mutation Description"""
              someMutation(input: SomeMutationInput!): SomeMutationPayload @deprecated(reason: "Just because")
            }

            type SomeMutationPayload {
              result: Int
              clientMutationId: String
            }

            input SomeMutationInput {
              clientMutationId: String
            }
            '''  # noqa: E501
        )
