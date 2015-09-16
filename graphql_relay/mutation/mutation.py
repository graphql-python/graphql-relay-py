from graphql.core.type import (
    GraphQLArgument,
    GraphQLInputObjectType,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
    GraphQLField,
)
from graphql.core.error import GraphQLError

def mutationWithClientMutationId(name, inputFields, outputFields, mutateAndGetPayload):
    augmentedInputFields = dict(inputFields,
        clientMutationId=GraphQLField(GraphQLNonNull(GraphQLString))
    )
    augmentedOutputFields = dict(outputFields,
        clientMutationId=GraphQLField(GraphQLNonNull(GraphQLString))
    )
    inputType = GraphQLInputObjectType(
        name+'Input',
        fields=augmentedInputFields,
    )
    outputType = GraphQLObjectType(
        name+'Payload',
        fields=augmentedOutputFields,
    )

    def resolver(__, args, info, *_):
        input = args.get('input')
        if not input:
            # TODO: Should be raised by Graphql
            raise GraphQLError('Input not provided')
        payload = mutateAndGetPayload(input, info)
        try:
            payload.clientMutationId = input['clientMutationId']
        except:
            raise GraphQLError('Cannot set clientMutationId in the payload object %s'%repr(payload))
        return payload

    return GraphQLField(
        outputType,
        args={
            'input': GraphQLArgument(GraphQLNonNull(inputType)),
        },
        resolver=resolver
    )
