from graphql import graphql_sync

from .star_wars_schema import star_wars_schema as schema


def describe_star_wars_mutations():
    def correctly_mutates_dataset():
        source = """
          mutation ($input: IntroduceShipInput!) {
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
        variable_values = {
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
        result = graphql_sync(schema, source, variable_values=variable_values)
        assert result == (expected, None)
