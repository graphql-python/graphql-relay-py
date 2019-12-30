from pytest import mark  # type: ignore

from graphql import graphql

from .star_wars_schema import StarWarsSchema


@mark.asyncio
async def test_correctly_mutates_dataset():
    query = """
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
    """
    params = {
        "input": {"shipName": "B-Wing", "factionId": "1", "clientMutationId": "abcde"}
    }
    expected = {
        "introduceShip": {
            "ship": {"id": "U2hpcDo5", "name": "B-Wing"},
            "faction": {"name": "Alliance to Restore the Republic"},
            "clientMutationId": "abcde",
        }
    }
    result = await graphql(StarWarsSchema, query, variable_values=params)
    assert result == (expected, None)
