import binascii
from typing import Any, Collection, Optional, TypeVar

from ..utils.base64 import base64, unbase64
from .connectiontypes import (
    Connection, ConnectionArguments, ConnectionCursor, Edge, PageInfo)

__all__ = [
    'connection_from_array', 'connection_from_array_slice',
    'cursor_for_object_in_connection', 'cursor_to_offset',
    'get_offset_with_default', 'offset_to_cursor'
]

T = TypeVar('T')


def connection_from_array(
        data: Collection, args: ConnectionArguments) -> Connection:
    """Create a connection argument from a collection.

    A simple function that accepts a collection (e.g. a Python list) and connection
    arguments, and returns a connection object for use in GraphQL. It uses array
    offsets as pagination, so pagination will only work if the array is static.
    """
    return connection_from_array_slice(
        data, args,
        slice_start=0,
        array_length=len(data),
    )


def connection_from_array_slice(
        array_slice: Collection, args: ConnectionArguments,
        slice_start: int, array_length: int
        ) -> Connection:
    """Given a slice of a collection, returns a connection object for use in GraphQL.

    This function is similar to `connection_from_array`, but is intended for use
    cases where you know the cardinality of the connection, consider it too large
    to materialize the entire collection, and instead wish pass in a slice of the
    total result large enough to cover the range specified in `args`.
    """
    before = args.get('before')
    after = args.get('after')
    first = args.get('first')
    last = args.get('last')
    slice_end = slice_start + len(array_slice)
    before_offset = get_offset_with_default(before, array_length)
    after_offset = get_offset_with_default(after, -1)

    start_offset = max(slice_start - 1, after_offset, -1) + 1
    end_offset = min(slice_end, before_offset, array_length)

    if isinstance(first, int):
        if first < 0:
            raise ValueError("Argument 'first' must be a non-negative integer.")

        end_offset = min(end_offset, start_offset + first)
    if isinstance(last, int):
        if last < 0:
            raise ValueError("Argument 'last' must be a non-negative integer.")

        start_offset = max(start_offset, end_offset - last)

    # If supplied slice is too large, trim it down before mapping over it.
    trimmed_slice = array_slice[
        max(start_offset - slice_start, 0):
        len(array_slice) - (slice_end - end_offset)
    ]

    edges = [
        Edge(
            node=value,
            cursor=offset_to_cursor(start_offset + index)
        )
        for index, value in enumerate(trimmed_slice)
    ]

    first_edge_cursor = edges[0].cursor if edges else None
    last_edge_cursor = edges[-1].cursor if edges else None
    lower_bound = after_offset + 1 if after else 0
    upper_bound = before_offset if before else array_length

    return Connection(
        edges=edges,
        pageInfo=PageInfo(
            startCursor=first_edge_cursor,
            endCursor=last_edge_cursor,
            hasPreviousPage=isinstance(last, int) and start_offset > lower_bound,
            hasNextPage=isinstance(first, int) and end_offset < upper_bound
        )
    )


PREFIX = 'arrayconnection:'


def offset_to_cursor(offset: int) -> ConnectionCursor:
    """Create the cursor string from an offset."""
    return base64(f"{PREFIX}{offset}")


def cursor_to_offset(cursor: ConnectionCursor) -> Optional[int]:
    """Rederive the offset from the cursor string."""
    try:
        return int(unbase64(cursor)[len(PREFIX):])
    except binascii.Error:
        return None


def cursor_for_object_in_connection(data: Collection, obj: T) -> Optional[Any]:
    """Return the cursor associated with an object in a collection."""
    try:
        # noinspection PyUnresolvedReferences
        offset = data.index(obj)  # type: ignore
    except AttributeError:  # collection does not have an index method
        for offset, value in data:
            if value == obj:
                return offset
        return None
    except ValueError:
        return None
    else:
        return offset_to_cursor(offset)


def get_offset_with_default(cursor: ConnectionCursor = None, default_offset=0) -> int:
    """Get offset from a given cursor and a default.

    Given an optional cursor and a default offset, return the offset to use;
    if the cursor contains a valid offset, that will be used,
    otherwise it will be the default.
    """
    if not isinstance(cursor, str):
        return default_offset

    offset = cursor_to_offset(cursor)
    return default_offset if offset is None else offset
