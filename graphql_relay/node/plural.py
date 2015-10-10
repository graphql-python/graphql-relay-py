from graphql.core.type import (
    GraphQLArgument,
    GraphQLList,
    GraphQLNonNull,
    GraphQLField
)
# GraphQLInputObjectType


def plural_identifying_root_field(arg_name, input_type, output_type, resolve_single_input, description=None):
    input_args = {}
    input_args[arg_name] = GraphQLArgument(
        GraphQLNonNull(
            GraphQLList(
                GraphQLNonNull(input_type)
            )
        )
    )

    def resolver(obj, args, *_):
        inputs = args[arg_name]
        return map(resolve_single_input, inputs)

    return GraphQLField(
        GraphQLList(output_type),
        description=description,
        args=input_args,
        resolver=resolver
    )
