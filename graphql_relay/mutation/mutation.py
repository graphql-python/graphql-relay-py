from graphql.core.type import (
    GraphQLArgument,
    GraphQLInputObjectField,
    GraphQLInputObjectType,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
    GraphQLField,
)
from graphql.core.error import GraphQLError


def mutation_with_client_mutation_id(name, input_fields, output_fields, mutate_and_get_payload):
    augmented_input_fields = dict(input_fields,
                                  clientMutationId=GraphQLInputObjectField(
                                      GraphQLNonNull(GraphQLString))
                                  )
    augmented_output_fields = dict(output_fields,
                                   clientMutationId=GraphQLField(
                                       GraphQLNonNull(GraphQLString))
                                   )
    input_type = GraphQLInputObjectType(
        name + 'Input',
        fields=augmented_input_fields,
    )
    output_type = GraphQLObjectType(
        name + 'Payload',
        fields=augmented_output_fields,
    )

    def resolver(__, args, info, *_):
        input = args.get('input')
        if not input:
            # TODO: Should be raised by Graphql
            raise GraphQLError('Input not provided')
        payload = mutate_and_get_payload(input, info)
        try:
            payload.clientMutationId = input['clientMutationId']
        except:
            raise GraphQLError(
                'Cannot set clientMutationId in the payload object %s' % repr(payload))
        return payload

    return GraphQLField(
        output_type,
        args={
            'input': GraphQLArgument(GraphQLNonNull(input_type)),
        },
        resolver=resolver
    )
