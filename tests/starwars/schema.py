from collections import namedtuple

from graphql.core.type import (
    GraphQLID,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
    GraphQLField
)

from graphql_relay.node.node import (
    nodeDefinitions,
    globalIdField,
    fromGlobalId
)

from graphql_relay.connection.arrayconnection import (
    connectionFromArray
)

from graphql_relay.connection.connection import (
    connectionArgs,
    connectionDefinitions
)

from graphql_relay.mutation.mutation import (
    mutationWithClientMutationId
)

from .data import (
    Faction,
    Ship,
    getFaction,
    getShip,
    getRebels,
    getEmpire,
    createShip,
)

# This is a basic end-to-end test, designed to demonstrate the various
# capabilities of a Relay-compliant GraphQL server.
# 
# It is recommended that readers of this test be familiar with
# the end-to-end test in GraphQL.js first, as this test skips
# over the basics covered there in favor of illustrating the
# key aspects of the Relay spec that this test is designed to illustrate.
#
# We will create a GraphQL schema that describes the major
# factions and ships in the original Star Wars trilogy.
#
# NOTE: This may contain spoilers for the original Star
# Wars trilogy.

# Using our shorthand to describe type systems, the type system for our
# example will be the followng:
#
# interface Node {
#   id: ID!
# }
#
# type Faction : Node {
#   id: ID!
#   name: String
#   ships: ShipConnection
# }
#
# type Ship : Node {
#   id: ID!
#   name: String
# }
#
# type ShipConnection {
#   edges: [ShipEdge]
#   pageInfo: PageInfo!
# }
#
# type ShipEdge {
#   cursor: String!
#   node: Ship
# }
#
# type PageInfo {
#   hasNextPage: Boolean!
#   hasPreviousPage: Boolean!
#   startCursor: String
#   endCursor: String
# }
#
# type Query {
#   rebels: Faction
#   empire: Faction
#   node(id: ID!): Node
# }
#
# input IntroduceShipInput {
#   clientMutationId: string!
#   shipName: string!
#   factionId: ID!
# }
#
# input IntroduceShipPayload {
#   clientMutationId: string!
#   ship: Ship
#   faction: Faction
# }
#
# type Mutation {
#   introduceShip(input IntroduceShipInput!): IntroduceShipPayload
# }

# We get the node interface and field from the relay library.
#
# The first method is the way we resolve an ID to its object. The second is the
# way we resolve an object that implements node to its type.
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


# We define our basic ship type.
#
# This implements the following type system shorthand:
#   type Ship : Node {
#     id: String!
#     name: String
#   }
shipType = GraphQLObjectType(
    name='Ship',
    description= 'A ship in the Star Wars saga',
    fields=lambda: {
        'id': globalIdField('Ship'),
        'name': GraphQLField(
            GraphQLString,
            description= 'The name of the ship.',
        )
    },
    interfaces= [nodeInterface]
)

# We define a connection between a faction and its ships.
#
# connectionType implements the following type system shorthand:
#   type ShipConnection {
#     edges: [ShipEdge]
#     pageInfo: PageInfo!
#   }
#
# connectionType has an edges field - a list of edgeTypes that implement the
# following type system shorthand:
#   type ShipEdge {
#     cursor: String!
#     node: Ship
#   }
shipConnection = connectionDefinitions('Ship', shipType).connectionType

# We define our faction type, which implements the node interface.
#
# This implements the following type system shorthand:
#   type Faction : Node {
#     id: String!
#     name: String
#     ships: ShipConnection
#   }
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

# This is the type that will be the root of our query, and the
# entry point into our schema.
#
# This implements the following type system shorthand:
#   type Query {
#     rebels: Faction
#     empire: Faction
#     node(id: String!): Node
#   }
queryType = GraphQLObjectType(
    name= 'Query',
    fields= lambda: {
        'rebels': GraphQLField(
            factionType,
            resolver= lambda *_: getRebels(),
        ),
        'empire': GraphQLField(
            factionType,
            resolver= lambda *_: getEmpire(),
        ),
        'node': nodeField
    }
)

# This will return a GraphQLFieldConfig for our ship
# mutation.
#
# It creates these two types implicitly:
#   input IntroduceShipInput {
#     clientMutationId: string!
#     shipName: string!
#     factionId: ID!
#   }
#
#   input IntroduceShipPayload {
#     clientMutationId: string!
#     ship: Ship
#     faction: Faction
#   }
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

# This is the type that will be the root of our mutations, and the
# entry point into performing writes in our schema.
#
# This implements the following type system shorthand:
#   type Mutation {
#     introduceShip(input IntroduceShipInput!): IntroduceShipPayload
#   }
mutationType = GraphQLObjectType(
    'Mutation',
    fields= lambda: {
        'introduceShip': shipMutation
    }
)

# Finally, we construct our schema (whose starting query type is the query
# type we defined above) and export it.
StarWarsSchema = GraphQLSchema(
    query= queryType,
    mutation= mutationType
)