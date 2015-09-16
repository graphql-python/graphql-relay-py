from graphql.core.type import (
    GraphQLArgument,
    GraphQLList,
    GraphQLNonNull,
    GraphQLField,
    GraphQLInputObjectType
)
# GraphQLInputObjectType

def pluralIdentifyingRootField(argName, inputType, outputType, resolveSingleInput, description=None):
    inputArgs = {}
    inputArgs[argName] = GraphQLArgument(
        GraphQLNonNull(
            GraphQLList(
                GraphQLNonNull(inputType)
            )
        )
    )
    def resolver(obj, args, *_):
        inputs = args[argName]
        return map(resolveSingleInput, inputs)

    return GraphQLField(
        GraphQLList(outputType),
        description=description,
        args=inputArgs,
        resolver=resolver 
    )
