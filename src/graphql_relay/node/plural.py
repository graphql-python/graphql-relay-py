from typing import Any, Callable, cast

from graphql.type import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInputType,
    GraphQLOutputType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLResolveInfo,
    is_non_null_type,
)


def plural_identifying_root_field(
    arg_name: str,
    input_type: GraphQLInputType,
    output_type: GraphQLOutputType,
    resolve_single_input: Callable[[GraphQLResolveInfo, str], Any],
    description: str = None,
) -> GraphQLField:
    if is_non_null_type(input_type):
        input_type = cast(GraphQLNonNull, input_type).of_type

    def resolve(_obj, info, **args):
        inputs = args[arg_name]
        return [resolve_single_input(info, input_) for input_ in inputs]

    return GraphQLField(
        GraphQLList(output_type),
        description=description,
        args={
            arg_name: GraphQLArgument(
                GraphQLNonNull(GraphQLList(GraphQLNonNull(input_type)))
            )
        },
        resolve=resolve,
    )
