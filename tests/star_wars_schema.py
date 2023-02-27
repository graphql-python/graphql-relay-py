from graphql import (
    GraphQLID,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLInputField,
    GraphQLSchema,
    GraphQLString,
    GraphQLField,
)

from graphql_relay.node.node import node_definitions, global_id_field, from_global_id
from graphql_relay.connection.array_connection import connection_from_array
from graphql_relay.connection.connection import connection_args, connection_definitions
from graphql_relay.mutation.mutation import mutation_with_client_mutation_id

from .star_wars_data import (
    Faction,
    get_faction,
    get_ship,
    get_rebels,
    get_empire,
    create_ship,
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
# example will be the following:
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
#   clientMutationId: string
#   shipName: string!
#   factionId: ID!
# }
#
# type IntroduceShipPayload {
#   clientMutationId: string
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


def get_node(global_id, _info):
    type_, id_ = from_global_id(global_id)
    if type_ == "Faction":
        return get_faction(id_)
    if type_ == "Ship":
        return get_ship(id_)
    return None  # pragma: no cover


def get_node_type(obj, _info, _type):
    if isinstance(obj, Faction):
        return faction_type.name
    return ship_type.name


node_interface, node_field = node_definitions(get_node, get_node_type)[:2]


# We define our basic ship type.
#
# This implements the following type system shorthand:
#   type Ship : Node {
#     id: String!
#     name: String
#   }
ship_type = GraphQLObjectType(
    name="Ship",
    description="A ship in the Star Wars saga",
    fields=lambda: {
        "id": global_id_field("Ship"),
        "name": GraphQLField(GraphQLString, description="The name of the ship."),
    },
    interfaces=[node_interface],
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
ship_edge, ship_connection = connection_definitions(ship_type, "Ship")

# We define our faction type, which implements the node interface.
#
# This implements the following type system shorthand:
#   type Faction : Node {
#     id: String!
#     name: String
#     ships: ShipConnection
#   }
faction_type = GraphQLObjectType(
    name="Faction",
    description="A faction in the Star Wars saga",
    fields=lambda: {
        "id": global_id_field("Faction"),
        "name": GraphQLField(GraphQLString, description="The name of the faction."),
        "ships": GraphQLField(
            ship_connection,
            description="The ships used by the faction.",
            args=connection_args,
            resolve=lambda faction, _info, **args: connection_from_array(
                [get_ship(ship) for ship in faction.ships], args
            ),
        ),
    },
    interfaces=[node_interface],
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
query_type = GraphQLObjectType(
    name="Query",
    fields=lambda: {
        "rebels": GraphQLField(faction_type, resolve=lambda _obj, _info: get_rebels()),
        "empire": GraphQLField(faction_type, resolve=lambda _obj, _info: get_empire()),
        "node": node_field,
    },
)

# This will return a GraphQLFieldConfig for our ship
# mutation.
#
# It creates these two types implicitly:
#   input IntroduceShipInput {
#     clientMutationId: string
#     shipName: string!
#     factionId: ID!
#   }
#
#   type IntroduceShipPayload {
#     clientMutationId: string
#     ship: Ship
#     faction: Faction
#   }


class IntroduceShipMutation:
    # noinspection PyPep8Naming
    def __init__(self, shipId, factionId, clientMutationId=None):
        self.shipId = shipId
        self.factionId = factionId
        self.clientMutationId = clientMutationId


# noinspection PyPep8Naming
def mutate_and_get_payload(_info, shipName, factionId, **_input):
    new_ship = create_ship(shipName, factionId)
    return IntroduceShipMutation(shipId=new_ship.id, factionId=factionId)


ship_mutation = mutation_with_client_mutation_id(
    "IntroduceShip",
    input_fields={
        "shipName": GraphQLInputField(GraphQLNonNull(GraphQLString)),
        "factionId": GraphQLInputField(GraphQLNonNull(GraphQLID)),
    },
    output_fields={
        "ship": GraphQLField(
            ship_type, resolve=lambda payload, _info: get_ship(payload.shipId)
        ),
        "faction": GraphQLField(
            faction_type, resolve=lambda payload, _info: get_faction(payload.factionId)
        ),
    },
    mutate_and_get_payload=mutate_and_get_payload,
)

# This is the type that will be the root of our mutations, and the
# entry point into performing writes in our schema.
#
# This implements the following type system shorthand:
#   type Mutation {
#     introduceShip(input IntroduceShipInput!): IntroduceShipPayload
#   }
mutation_type = GraphQLObjectType(
    "Mutation", fields=lambda: {"introduceShip": ship_mutation}
)

# Finally, we construct our schema (whose starting query type is the query
# type we defined above) and export it.
star_wars_schema = GraphQLSchema(query=query_type, mutation=mutation_type)
