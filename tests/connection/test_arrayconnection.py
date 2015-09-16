from pytest import raises
from graphql_relay.connection.arrayconnection import (
    connectionFromArray, cursorForObjectInConnection)

letters = ['A', 'B', 'C', 'D', 'E']

def test_returns_all_elements_without_filters():
    c = connectionFromArray(letters, {})
    expected = {
        'edges': [
          {
            'node': 'A',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          },
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
          {
            'node': 'E',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_respects_a_smaller_first():
    c = connectionFromArray(letters, first=2)
    expected = {
        'edges': [
          {
            'node': 'A',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          },
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          'hasPreviousPage': False,
          'hasNextPage': True,
        }
    }
    assert c.to_dict() == expected

def test_respects_an_overly_large_first():
    c = connectionFromArray(letters, first=10)
    expected = {
        'edges': [
          {
            'node': 'A',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          },
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
          {
            'node': 'E',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_respects_a_smaller_last():
    c = connectionFromArray(letters, last=2)
    expected = {
        'edges': [
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
          {
            'node': 'E',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          'hasPreviousPage': True,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_respects_an_overly_large_last():
    c = connectionFromArray(letters, last=10)
    expected = {
        'edges': [
          {
            'node': 'A',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          },
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
          {
            'node': 'E',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_pagination_respects_first_after():
    c = connectionFromArray(letters, first=2, after='YXJyYXljb25uZWN0aW9uOjE=')
    expected = {
        'edges': [
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          'hasPreviousPage': False,
          'hasNextPage': True,
        }
    }
    assert c.to_dict() == expected

def test_pagination_respects_longfirst_after():
    c = connectionFromArray(letters, first=10, after='YXJyYXljb25uZWN0aW9uOjE=')
    expected = {
        'edges': [
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
          {
            'node': 'E',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_pagination_respects_last_before():
    c = connectionFromArray(letters, last=2, before='YXJyYXljb25uZWN0aW9uOjM=')
    expected = {
        'edges': [
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          'hasPreviousPage': True,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_pagination_respects_longlast_before():
    c = connectionFromArray(letters, last=10, before='YXJyYXljb25uZWN0aW9uOjM=')
    expected = {
        'edges': [
          {
            'node': 'A',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          },
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_first_after_before_few():
    c = connectionFromArray(letters, first=2,
        after='YXJyYXljb25uZWN0aW9uOjA=',
        before='YXJyYXljb25uZWN0aW9uOjQ=',
    )
    expected = {
        'edges': [
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          'hasPreviousPage': False,
          'hasNextPage': True,
        }
    }
    assert c.to_dict() == expected

def test_first_after_before_many():
    c = connectionFromArray(letters, first=4,
        after='YXJyYXljb25uZWN0aW9uOjA=',
        before='YXJyYXljb25uZWN0aW9uOjQ=',
    )
    expected = {
        'edges': [
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_first_after_before_exact():
    c = connectionFromArray(letters, first=3,
        after='YXJyYXljb25uZWN0aW9uOjA=',
        before='YXJyYXljb25uZWN0aW9uOjQ=',
    )
    expected = {
        'edges': [
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_last_after_before_few():
    c = connectionFromArray(letters, last=2,
        after='YXJyYXljb25uZWN0aW9uOjA=',
        before='YXJyYXljb25uZWN0aW9uOjQ=',
    )
    expected = {
        'edges': [
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          'hasPreviousPage': True,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_last_after_before_many():
    c = connectionFromArray(letters, last=4,
        after='YXJyYXljb25uZWN0aW9uOjA=',
        before='YXJyYXljb25uZWN0aW9uOjQ=',
    )
    expected = {
        'edges': [
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_last_after_before_exact():
    c = connectionFromArray(letters, last=3,
        after='YXJyYXljb25uZWN0aW9uOjA=',
        before='YXJyYXljb25uZWN0aW9uOjQ=',
    )
    expected = {
        'edges': [
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_no_elements_first_0():
    c = connectionFromArray(letters, first=0)
    expected = {
        'edges': [
        ],
        'pageInfo': {
          'startCursor': None,
          'endCursor': None,
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_all_elements_invalid_cursors():
    c = connectionFromArray(letters, before='invalid', after='invalid')
    expected = {
        'edges': [
          {
            'node': 'A',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          },
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
          {
            'node': 'E',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_all_elements_cursor_outside():
    c = connectionFromArray(letters,
        before='YXJyYXljb25uZWN0aW9uOjYK',
        after='YXJyYXljb25uZWN0aW9uOi0xCg==')
    expected = {
        'edges': [
          {
            'node': 'A',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          },
          {
            'node': 'B',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
          },
          {
            'node': 'C',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjI=',
          },
          {
            'node': 'D',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjM=',
          },
          {
            'node': 'E',
            'cursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          },
        ],
        'pageInfo': {
          'startCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
          'endCursor': 'YXJyYXljb25uZWN0aW9uOjQ=',
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_no_elements_cursors_cross():
    c = connectionFromArray(letters, 
        before='YXJyYXljb25uZWN0aW9uOjI=',
        after='YXJyYXljb25uZWN0aW9uOjQ=')
    expected = {
        'edges': [
        ],
        'pageInfo': {
          'startCursor': None,
          'endCursor': None,
          'hasPreviousPage': False,
          'hasNextPage': False,
        }
    }
    assert c.to_dict() == expected

def test_cursorForObjectInConnection_member_object():
    letterBCursor = cursorForObjectInConnection(letters, 'B')
    assert letterBCursor == 'YXJyYXljb25uZWN0aW9uOjE='

def test_cursorForObjectInConnection_non_member_object():
    letterBCursor = cursorForObjectInConnection(letters, 'F')
    assert letterBCursor == None
