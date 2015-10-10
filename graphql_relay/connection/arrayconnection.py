from graphql_relay.utils import base64, unbase64

from .connectiontypes import Connection, PageInfo, Edge


def connection_from_list(data, args={}, **kwargs):
    '''
    A simple function that accepts an array and connection arguments, and returns
    a connection object for use in GraphQL. It uses array offsets as pagination,
    so pagination will only work if the array is static.
    '''
    full_args = dict(args, **kwargs)

    before = full_args.get('before')
    after = full_args.get('after')
    first = full_args.get('first')
    last = full_args.get('last')

    count = len(data)
    # Slice with cursors
    begin = max(get_offset(after, -1), -1) + 1
    end = min(get_offset(before, count + 1), count)
    if begin >= count or begin >= end:
        return empty_connection()

    # Save the pre-slice cursors
    first_preslice_cursor = offset_to_cursor(begin)
    last_preslice_cursor = offset_to_cursor(min(end, count) - 1)

    # Slice with limits
    if first is not None:
        end = min(begin + first, end)
    if last is not None:
        begin = max(end - last, begin)

    if begin >= count or begin >= end:
        return empty_connection()

    sliced_data = data[begin:end]
    edges = [
        Edge(node, cursor=offset_to_cursor(i + begin))
        for i, node in enumerate(sliced_data)
    ]

    # Construct the connection
    first_edge = edges[0]
    last_edge = edges[len(edges) - 1]
    return Connection(
        edges,
        PageInfo(
            startCursor=first_edge.cursor,
            endCursor=last_edge.cursor,
            hasPreviousPage=(first_edge.cursor != first_preslice_cursor),
            hasNextPage=(last_edge.cursor != last_preslice_cursor)
        )
    )


def connection_from_promised_list(data_promise, args={}, **kwargs):
    '''
    A version of the above that takes a promised array, and returns a promised
    connection.
    '''
    # TODO: Promises not implemented
    raise Exception('connection_from_promised_list is not implemented yet')
    # return dataPromise.then(lambda data:connection_from_list(data, args))


def empty_connection():
    '''
    Helper to get an empty connection.
    '''
    return Connection(
        [],
        PageInfo(
            startCursor=None,
            endCursor=None,
            hasPreviousPage=False,
            hasNextPage=False,
        )
    )


PREFIX = 'arrayconnection:'


def offset_to_cursor(offset):
    '''
    Creates the cursor string from an offset.
    '''
    return base64(PREFIX + str(offset))


def cursor_to_offset(cursor):
    '''
    Rederives the offset from the cursor string.
    '''
    try:
        return int(unbase64(cursor)[len(PREFIX):len(PREFIX) + 10])
    except:
        return None


def cursor_for_object_in_connection(data, _object):
    '''
    Return the cursor associated with an object in an array.
    '''
    if _object not in data:
        return None

    offset = data.index(_object)
    return offset_to_cursor(offset)


def get_offset(cursor, default_offset=0):
    '''
    Given an optional cursor and a default offset, returns the offset
    to use; if the cursor contains a valid offset, that will be used,
    otherwise it will be the default.
    '''
    if cursor is None:
        return default_offset

    offset = cursor_to_offset(cursor)
    try:
        return int(offset)
    except:
        return default_offset
