"""The graphql_relay package"""

# The graphql-relay and graphql-relay-js version info
from .version import version, version_info, version_js, version_info_js

# Types for creating connection types in the schema
from .connection.connectiontypes import (
    Connection,
    ConnectionArguments,
    ConnectionCursor,
    Edge,
    PageInfo,
)

# Helpers for creating connection types in the schema
from .connection.connection import (
    backward_connection_args,
    connection_args,
    connection_definitions,
    forward_connection_args,
    GraphQLConnectionDefinitions,
)

# Helpers for creating connections from arrays
from .connection.arrayconnection import (
    connection_from_array,
    connection_from_array_slice,
    cursor_for_object_in_connection,
    cursor_to_offset,
    get_offset_with_default,
    offset_to_cursor,
)

# Helper for creating mutations with client mutation IDs
from .mutation.mutation import mutation_with_client_mutation_id

# Helper for creating node definitions
from .node.node import node_definitions

#  Helper for creating plural identifying root fields
from .node.plural import plural_identifying_root_field

# Utilities for creating global IDs in systems that don't have them
from .node.node import from_global_id, global_id_field, to_global_id

# Deprecated functions from older graphql-relay-py versions
# noinspection PyProtectedMember,PyUnresolvedReferences,PyDeprecation
from .connection.arrayconnection import (  # noqa: F401
    connection_from_list,
    connection_from_list_slice,
)

__version__ = version
__version_info__ = version_info
__version_js__ = version_js
__version_info_js__ = version_info_js

__all__ = [
    "version",
    "version_info",
    "version_js",
    "version_info_js",
    "Connection",
    "ConnectionArguments",
    "ConnectionCursor",
    "Edge",
    "PageInfo",
    "backward_connection_args",
    "connection_args",
    "connection_definitions",
    "forward_connection_args",
    "GraphQLConnectionDefinitions",
    "connection_from_array",
    "connection_from_array_slice",
    "cursor_for_object_in_connection",
    "cursor_to_offset",
    "get_offset_with_default",
    "offset_to_cursor",
    "mutation_with_client_mutation_id",
    "node_definitions",
    "plural_identifying_root_field",
    "from_global_id",
    "global_id_field",
    "to_global_id",
]
