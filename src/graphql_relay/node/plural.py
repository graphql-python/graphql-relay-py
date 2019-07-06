from graphql.type import (
    GraphQLArgument,
    GraphQLList,
    GraphQLNonNull,
    GraphQLField
)


def plural_identifying_root_field(
        arg_name, input_type, output_type,
        resolve_single_input, description=None):
    input_args = {arg_name: GraphQLArgument(
        GraphQLNonNull(GraphQLList(GraphQLNonNull(input_type))))}

    def resolve(_obj, info, **args):
        inputs = args[arg_name]
        return [resolve_single_input(info, input_) for input_ in inputs]

    return GraphQLField(
        GraphQLList(output_type),
        description=description,
        args=input_args,
        resolve=resolve)
