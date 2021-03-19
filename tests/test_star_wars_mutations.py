from graphql import graphql_sync

from .star_wars_schema import StarWarsSchema


def describe_star_wars_mutations():
    def correctly_mutates_dataset():
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
            "input": {
                "shipName": "B-Wing",
                "factionId": "1",
                "clientMutationId": "abcde",
            }
        }
        expected = {
            "introduceShip": {
                "ship": {"id": "U2hpcDo5", "name": "B-Wing"},
                "faction": {"name": "Alliance to Restore the Republic"},
                "clientMutationId": "abcde",
            }
        }
        result = graphql_sync(StarWarsSchema, query, variable_values=params)
        assert result == (expected, None)
