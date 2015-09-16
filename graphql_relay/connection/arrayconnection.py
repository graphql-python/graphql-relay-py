from base64 import b64encode as base64, b64decode as unbase64

from .connectiontypes import Connection, PageInfo, Edge


def connectionFromArray(data, args={}, **kwargs):
    '''
    A simple function that accepts an array and connection arguments, and returns
    a connection object for use in GraphQL. It uses array offsets as pagination,
    so pagination will only work if the array is static.
    '''
    edges = [Edge(value, cursor=offsetToCursor(index)) for index, value in enumerate(data)]
    full_args = dict(args, **kwargs)

    before = full_args.get('before')
    after = full_args.get('after')
    first = full_args.get('first')
    last = full_args.get('last')

    # Slice with cursors
    begin = max(getOffset(after, -1), -1) + 1;
    end = min(getOffset(before, len(edges) + 1), len(edges) + 1);
    edges = edges[begin:end]
    if len(edges) == 0:
        return emptyConnection()

    # Save the pre-slice cursors
    firstPresliceCursor = edges[0].cursor
    lastPresliceCursor = edges[len(edges) - 1].cursor

    # Slice with limits
    if first != None:
        edges = edges[0:first]
    if last != None:
        edges = edges[-last:]
    
    if len(edges) == 0:
        return emptyConnection()

    # Construct the connection
    firstEdge = edges[0];
    lastEdge = edges[len(edges) - 1];
    return Connection(
        edges,
        PageInfo(
            startCursor=firstEdge.cursor,
            endCursor=lastEdge.cursor,
            hasPreviousPage= (firstEdge.cursor != firstPresliceCursor),
            hasNextPage= (lastEdge.cursor != lastPresliceCursor)
        )
    )


def connectionFromPromisedArray(dataPromise, args={}, **kwargs):
    '''
    A version of the above that takes a promised array, and returns a promised
    connection.
    '''
    # TODO: Promises not implemented
    raise Exception('connectionFromPromisedArray is not implemented yet')
    # return dataPromise.then(lambda data:connectionFromArray(data, args))


def emptyConnection():
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


PREFIX = 'arrayconnection:';


def offsetToCursor(offset):
    '''
    Creates the cursor string from an offset.
    '''
    return base64(PREFIX + str(offset));


def cursorToOffset(cursor):
    '''
    Rederives the offset from the cursor string.
    '''
    try:
        return int(unbase64(cursor)[len(PREFIX):len(PREFIX)+10])
    except:
        return None

def cursorForObjectInConnection(data, _object):
    '''
    Return the cursor associated with an object in an array.
    '''
    if _object not in data:
        return None

    offset = data.index(_object)
    return offsetToCursor(offset)


def getOffset(cursor, defaultOffset=0):
    '''
    Given an optional cursor and a default offset, returns the offset
    to use; if the cursor contains a valid offset, that will be used,
    otherwise it will be the default.
    '''
    if cursor == None:
        return defaultOffset

    offset = cursorToOffset(cursor)
    try:
        return int(offset)
    except:
        return defaultOffset
