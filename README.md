# Relay Library for GraphQL Python

This is a library to allow the easy creation of Relay-compliant servers using
the [GraphQL Python](https://github.com/graphql-python/graphql-core) reference implementation
of a GraphQL server.

*Note: The code is a __exact__ port of the original [graphql-relay js implementation](https://github.com/graphql/graphql-relay-js)
from Facebook*

[![Build Status](https://travis-ci.org/graphql-python/graphql-relay-py.svg?branch=master)](https://travis-ci.org/graphql-python/graphql-relay-py)
[![Coverage Status](https://coveralls.io/repos/graphql-python/graphql-relay-py/badge.svg?branch=master&service=github)](https://coveralls.io/github/graphql-python/graphql-relay-py?branch=master)

## Getting Started

A basic understanding of GraphQL and of the GraphQL Python implementation is needed
to provide context for this library.

An overview of GraphQL in general is available in the
[README](https://github.com/graphql-python/graphql-core/blob/master/README.md) for the
[Specification for GraphQL](https://github.com/graphql-python/graphql-core).

This library is designed to work with the 
the [GraphQL Python](https://github.com/graphql-python/graphql-core) reference implementation
of a GraphQL server.

An overview of the functionality that a Relay-compliant GraphQL server should
provide is in the [GraphQL Relay Specification](https://facebook.github.io/relay/docs/graphql-relay-specification.html)
on the [Relay website](https://facebook.github.io/relay/). That overview
describes a simple set of examples that exist as [tests](tests) in this
repository. A good way to get started with this repository is to walk through
that documentation and the corresponding tests in this library together.

## Using Relay Library for GraphQL Python (graphql-core)

Install Relay Library for GraphQL Python

```sh
pip install graphql-core --pre # Last version of graphql-core
pip install graphql-relay
```

When building a schema for [GraphQL](https://github.com/graphql-python/graphql-core),
the provided library functions can be used to simplify the creation of Relay
patterns.

### Connections 

Helper functions are provided for both building the GraphQL types
for connections and for implementing the `resolver` method for fields
returning those types.

 - `connectionArgs` returns the arguments that fields should provide when
they return a connection type.
 - `connectionDefinitions` returns a `connectionType` and its associated
`edgeType`, given a name and a node type.
 - `connectionFromArray` is a helper method that takes an array and the
arguments from `connectionArgs`, does pagination and filtering, and returns
an object in the shape expected by a `connectionType`'s `resolver` function.
 - `connectionFromPromisedArray` is similar to `connectionFromArray`, but
it takes a promise that resolves to an array, and returns a promise that
resolves to the expected shape by `connectionType`.
 - `cursorForObjectInConnection` is a helper method that takes an array and a
member object, and returns a cursor for use in the mutation payload.

An example usage of these methods from the [test schema](tests/starwars/schema.py):

```python
shipConnection = connectionDefinitions('Ship', shipType).connectionType

factionType = GraphQLObjectType(
    name= 'Faction',
    description= 'A faction in the Star Wars saga',
    fields= lambda: {
        'id': globalIdField('Faction'),
        'name': GraphQLField(
            GraphQLString,
            description='The name of the faction.',
        ),
        'ships': GraphQLField(
            shipConnection,
            description= 'The ships used by the faction.',
            args= connectionArgs,
            resolver= lambda faction, args, *_: connectionFromArray(
                map(getShip, faction.ships),
                args
            ),
        )
    },
    interfaces= [nodeInterface]
)
```

This shows adding a `ships` field to the `Faction` object that is a connection.
It uses `connectionDefinitions({name: 'Ship', nodeType: shipType})` to create
the connection type, adds `connectionArgs` as arguments on this function, and
then implements the resolver function by passing the array of ships and the
arguments to `connectionFromArray`.

### Object Identification

Helper functions are provided for both building the GraphQL types
for nodes and for implementing global IDs around local IDs.

 - `nodeDefinitions` returns the `Node` interface that objects can implement,
and returns the `node` root field to include on the query type. To implement
this, it takes a function to resolve an ID to an object, and to determine
the type of a given object.
 - `toGlobalId` takes a type name and an ID specific to that type name,
and returns a "global ID" that is unique among all types.
 - `fromGlobalId` takes the "global ID" created by `toGlobalID`, and retuns
the type name and ID used to create it.
 - `globalIdField` creates the configuration for an `id` field on a node.
 - `pluralIdentifyingRootField` creates a field that accepts a list of
non-ID identifiers (like a username) and maps then to their corresponding
objects.

An example usage of these methods from the [test schema](tests/starwars/schema.py):

```python
def getNode(globalId, *args):
    resolvedGlobalId = fromGlobalId(globalId)
    _type, _id = resolvedGlobalId.type, resolvedGlobalId.id
    if _type == 'Faction':
        return getFaction(_id)
    elif _type == 'Ship':
        return getShip(_id)
    else:
        return None

def getNodeType(obj):
    if isinstance(obj, Faction):
        return factionType
    else:
        return shipType

_nodeDefinitions = nodeDefinitions(getNode, getNodeType)
nodeField, nodeInterface = _nodeDefinitions.nodeField, _nodeDefinitions.nodeInterface

factionType = GraphQLObjectType(
    name= 'Faction',
    description= 'A faction in the Star Wars saga',
    fields= lambda: {
        'id': globalIdField('Faction'),
    },
    interfaces= [nodeInterface]
)

queryType = GraphQLObjectType(
    name= 'Query',
    fields= lambda: {
        'node': nodeField
    }
)
```

This uses `nodeDefinitions` to construct the `Node` interface and the `node`
field; it uses `fromGlobalId` to resolve the IDs passed in in the implementation
of the function mapping ID to object. It then uses the `globalIdField` method to
create the `id` field on `Faction`, which also ensures implements the
`nodeInterface`. Finally, it adds the `node` field to the query type, using the
`nodeField` returned by `nodeDefinitions`.

### Mutations

A helper function is provided for building mutations with
single inputs and client mutation IDs.

 - `mutationWithClientMutationId` takes a name, input fields, output fields,
and a mutation method to map from the input fields to the output fields,
performing the mutation along the way. It then creates and returns a field
configuration that can be used as a top-level field on the mutation type.

An example usage of these methods from the [test schema](tests/starwars/schema.py):

```python
class IntroduceShipMutation(object):
    def __init__(self, shipId, factionId, clientMutationId=None):
        self.shipId = shipId
        self.factionId = factionId
        self.clientMutationId = None

def mutateAndGetPayload(data, *_):
    shipName = data.get('shipName')
    factionId = data.get('factionId')
    newShip = createShip(shipName, factionId)
    return IntroduceShipMutation(
        shipId=newShip.id,
        factionId=factionId,
    )

shipMutation = mutationWithClientMutationId(
    'IntroduceShip',
    inputFields={
        'shipName': GraphQLField(
            GraphQLNonNull(GraphQLString)
        ),
        'factionId': GraphQLField(
            GraphQLNonNull(GraphQLID)
        )
    },
    outputFields= {
        'ship': GraphQLField(
            shipType,
            resolver= lambda payload, *_: getShip(payload.shipId)
        ),
        'faction': GraphQLField(
            factionType,
            resolver= lambda payload, *_: getFaction(payload.factionId)
        )
    },
    mutateAndGetPayload=mutateAndGetPayload
)

mutationType = GraphQLObjectType(
    'Mutation',
    fields= lambda: {
        'introduceShip': shipMutation
    }
)
```

This code creates a mutation named `IntroduceShip`, which takes a faction
ID and a ship name as input. It outputs the `Faction` and the `Ship` in
question. `mutateAndGetPayload` then gets an object with a property for
each input field, performs the mutation by constructing the new ship, then
returns an object that will be resolved by the output fields.

Our mutation type then creates the `introduceShip` field using the return
value of `mutationWithClientMutationId`.

## Contributing

After cloning this repo, ensure dependencies are installed by running:

```sh
python setup.py install
```

After developing, the full test suite can be evaluated by running:

```sh
python setup.py test # Use --pytest-args="-v -s" for verbose mode
```
