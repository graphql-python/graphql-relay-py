import warnings

# noinspection PyDeprecation
from .array_connection import (
    connection_from_array,
    connection_from_array_slice,
    cursor_for_object_in_connection,
    cursor_to_offset,
    get_offset_with_default,
    offset_to_cursor,
    SizedSliceable,
)

# Deprecated functions from older graphql-relay-py versions
# noinspection PyProtectedMember,PyUnresolvedReferences,PyDeprecation
from .array_connection import (  # noqa: F401
    connection_from_list,
    connection_from_list_slice,
)

warnings.warn(
    "The 'arrayconnection' module is deprecated. "
    "Functions should be imported from the top-level package instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "connection_from_array",
    "connection_from_array_slice",
    "cursor_for_object_in_connection",
    "cursor_to_offset",
    "get_offset_with_default",
    "offset_to_cursor",
    "SizedSliceable",
]
