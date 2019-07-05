from graphql import graphql

from .schema import StarWarsSchema


def test_correctly_mutates_dataset():
    query = '''
      mutation AddBWingQuery($input: IntroduceShipInput!) {
        introduceShip(input: $input) {
          ship {
            id
            name
          }
          faction {
            name
          }
          clientMutationId
        }
      }
    '''
    params = {
        'input': {
            'shipName': 'B-Wing',
            'factionId': '1',
            'clientMutationId': 'abcde',
        }
    }
    expected = {
        'introduceShip': {
            'ship': {
                'id': 'U2hpcDo5',
                'name': 'B-Wing'
            },
            'faction': {
                'name': 'Alliance to Restore the Republic'
            },
            'clientMutationId': 'abcde',
        }
    }
    result = graphql(StarWarsSchema, query, variables=params)
    assert not result.errors
    assert result.data == expected
