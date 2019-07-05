from graphql import graphql

from .schema import StarWarsSchema


def test_correct_fetch_first_ship_rebels():
    query = '''
    query RebelsShipsQuery {
      rebels {
        name,
        ships(first: 1) {
          edges {
            node {
              name
            }
          }
        }
      }
    }
    '''
    expected = {
        'rebels': {
            'name': 'Alliance to Restore the Republic',
            'ships': {
                'edges': [
                    {
                        'node': {
                            'name': 'X-Wing'
                        }
                    }
                ]
            }
        }
    }
    result = graphql(StarWarsSchema, query)
    assert not result.errors
    assert result.data == expected
