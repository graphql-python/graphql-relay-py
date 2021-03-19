from graphql import graphql_sync

from .star_wars_schema import StarWarsSchema as schema


def describe_star_wars_object_identification():
    def fetches_the_id_and_name_of_the_rebels():
        source = """
            {
              rebels {
                id
                name
              }
            }
            """
        expected = {
            "rebels": {"id": "RmFjdGlvbjox", "name": "Alliance to Restore the Republic"}
        }
        result = graphql_sync(schema, source)
        assert result == (expected, None)

    def refetches_the_rebels():
        source = """
            {
              node(id: "RmFjdGlvbjox") {
                id
                ... on Faction {
                  name
                }
              }
            }
            """
        expected = {
            "node": {"id": "RmFjdGlvbjox", "name": "Alliance to Restore the Republic"}
        }
        result = graphql_sync(schema, source)
        assert result == (expected, None)

    def fetches_the_id_and_name_of_the_empire():
        source = """
            {
              empire {
                id
                name
              }
            }
            """
        expected = {"empire": {"id": "RmFjdGlvbjoy", "name": "Galactic Empire"}}
        result = graphql_sync(schema, source)
        assert result == (expected, None)

    def refetches_the_empire():
        source = """
            {
              node(id: "RmFjdGlvbjoy") {
                id
                ... on Faction {
                  name
                }
              }
            }
            """
        expected = {"node": {"id": "RmFjdGlvbjoy", "name": "Galactic Empire"}}
        result = graphql_sync(schema, source)
        assert result == (expected, None)

    def refetches_the_x_wing():
        source = """
            {
              node(id: "U2hpcDox") {
                id
                ... on Ship {
                  name
                }
              }
            }
            """
        expected = {"node": {"id": "U2hpcDox", "name": "X-Wing"}}
        result = graphql_sync(schema, source)
        assert result == (expected, None)
