from collections import namedtuple

from graphql.core.type import (
    GraphQLID,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLInputObjectField,
    GraphQLSchema,
    GraphQLString,
    GraphQLField
)

from graphql_relay.node.node import (
    node_definitions,
    global_id_field,
    from_global_id
)

from graphql_relay.connection.arrayconnection import (
    connection_from_list
)

from graphql_relay.connection.connection import (
    connection_args,
    connection_definitions
)

from graphql_relay.mutation.mutation import (
    mutation_with_client_mutation_id
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


def get_node(global_id, *args):
    resolvedGlobalId = from_global_id(global_id)
    _type, _id = resolvedGlobalId.type, resolvedGlobalId.id
    if _type == 'Faction':
        return getFaction(_id)
    elif _type == 'Ship':
        return getShip(_id)
    else:
        return None


def get_node_type(obj, info):
    if isinstance(obj, Faction):
        return factionType
    else:
        return shipType

_node_definitions = node_definitions(get_node, get_node_type)
node_field, node_interface = _node_definitions.node_field, _node_definitions.node_interface


# We define our basic ship type.
#
# This implements the following type system shorthand:
#   type Ship : Node {
#     id: String!
#     name: String
#   }
shipType = GraphQLObjectType(
    name='Ship',
    description='A ship in the Star Wars saga',
    fields=lambda: {
        'id': global_id_field('Ship'),
        'name': GraphQLField(
            GraphQLString,
            description='The name of the ship.',
        )
    },
    interfaces=[node_interface]
)

# We define a connection between a faction and its ships.
#
# connection_type implements the following type system shorthand:
#   type ShipConnection {
#     edges: [ShipEdge]
#     pageInfo: PageInfo!
#   }
#
# connection_type has an edges field - a list of edgeTypes that implement the
# following type system shorthand:
#   type ShipEdge {
#     cursor: String!
#     node: Ship
#   }
shipConnection = connection_definitions('Ship', shipType).connection_type

# We define our faction type, which implements the node interface.
#
# This implements the following type system shorthand:
#   type Faction : Node {
#     id: String!
#     name: String
#     ships: ShipConnection
#   }
factionType = GraphQLObjectType(
    name='Faction',
    description='A faction in the Star Wars saga',
    fields=lambda: {
        'id': global_id_field('Faction'),
        'name': GraphQLField(
            GraphQLString,
            description='The name of the faction.',
        ),
        'ships': GraphQLField(
            shipConnection,
            description='The ships used by the faction.',
            args=connection_args,
            resolver=lambda faction, args, *_: connection_from_list(
                [getShip(ship) for ship in faction.ships],
                args
            ),
        )
    },
    interfaces=[node_interface]
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
    name='Query',
    fields=lambda: {
        'rebels': GraphQLField(
            factionType,
            resolver=lambda *_: getRebels(),
        ),
        'empire': GraphQLField(
            factionType,
            resolver=lambda *_: getEmpire(),
        ),
        'node': node_field
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


def mutate_and_get_payload(data, *_):
    shipName = data.get('shipName')
    factionId = data.get('factionId')
    newShip = createShip(shipName, factionId)
    return IntroduceShipMutation(
        shipId=newShip.id,
        factionId=factionId,
    )

shipMutation = mutation_with_client_mutation_id(
    'IntroduceShip',
    input_fields={
        'shipName': GraphQLInputObjectField(
            GraphQLNonNull(GraphQLString)
        ),
        'factionId': GraphQLInputObjectField(
            GraphQLNonNull(GraphQLID)
        )
    },
    output_fields={
        'ship': GraphQLField(
            shipType,
            resolver=lambda payload, *_: getShip(payload.shipId)
        ),
        'faction': GraphQLField(
            factionType,
            resolver=lambda payload, *_: getFaction(payload.factionId)
        )
    },
    mutate_and_get_payload=mutate_and_get_payload
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
    fields=lambda: {
        'introduceShip': shipMutation
    }
)

# Finally, we construct our schema (whose starting query type is the query
# type we defined above) and export it.
StarWarsSchema = GraphQLSchema(
    query=queryType,
    mutation=mutationType
)
