from inspect import isawaitable

from graphql.type import (
    GraphQLArgument,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
    GraphQLField,
)
from graphql.error import GraphQLError
from graphql.pyutils import inspect

from ..utils import resolve_maybe_thunk


def mutation_with_client_mutation_id(
        name, input_fields, output_fields, mutate_and_get_payload):
    augmented_input_fields = dict(
        resolve_maybe_thunk(input_fields),
        clientMutationId=GraphQLInputField(
            GraphQLNonNull(GraphQLString)))
    augmented_output_fields = dict(
        resolve_maybe_thunk(output_fields),
        clientMutationId=GraphQLField(
            GraphQLNonNull(GraphQLString)))
    input_type = GraphQLInputObjectType(
        name + 'Input',
        fields=augmented_input_fields)
    output_type = GraphQLObjectType(
        name + 'Payload',
        fields=augmented_output_fields)

    async def resolve(_root, info, **args):
        input_ = args.get('input') or {}
        payload = mutate_and_get_payload(info, **input_)
        if isawaitable(payload):
            payload = await payload
        try:
            payload.clientMutationId = input_['clientMutationId']
        except KeyError:
            raise GraphQLError(
                'Cannot set clientMutationId'
                f' in the payload object {inspect(payload)}.')
        return payload

    return GraphQLField(
        output_type,
        args={'input': GraphQLArgument(GraphQLNonNull(input_type))},
        resolve=resolve)
