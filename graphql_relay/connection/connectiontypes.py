class Connection(object):
    def __init__(self, edges, pageInfo):
        self.edges = edges
        self.pageInfo = pageInfo

    def to_dict(self):
        return {
            'edges': [e.to_dict() for e in self.edges],
            'pageInfo': self.pageInfo.to_dict(),
        }

class PageInfo(object):
    def __init__(self, startCursor="", endCursor="", hasPreviousPage=False, hasNextPage=False):
        self.startCursor = startCursor
        self.endCursor = endCursor
        self.hasPreviousPage = hasPreviousPage
        self.hasNextPage = hasNextPage

    def to_dict(self):
        return {
            'startCursor': self.startCursor,
            'endCursor': self.endCursor,
            'hasPreviousPage': self.hasPreviousPage,
            'hasNextPage': self.hasNextPage,
        }

class Edge(object):
    def __init__(self, node, cursor):
        self.node = node
        self.cursor = cursor

    def to_dict(self):
        return {
            'node': self.node,
            'cursor': self.cursor,
        }
