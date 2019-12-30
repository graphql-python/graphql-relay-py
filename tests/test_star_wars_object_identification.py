from pytest import mark  # type: ignore

from graphql import graphql

from .star_wars_schema import StarWarsSchema


@mark.asyncio
async def test_correctly_fetches_id_name_rebels():
    query = """
      query RebelsQuery {
        rebels {
          id
          name
        }
      }
    """
    expected = {
        "rebels": {"id": "RmFjdGlvbjox", "name": "Alliance to Restore the Republic"}
    }
    result = await graphql(StarWarsSchema, query)
    assert result == (expected, None)


@mark.asyncio
async def test_correctly_refetches_rebels():
    query = """
      query RebelsRefetchQuery {
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
    result = await graphql(StarWarsSchema, query)
    assert result == (expected, None)


@mark.asyncio
async def test_correctly_fetches_id_name_empire():
    query = """
      query EmpireQuery {
        empire {
          id
          name
        }
      }
    """
    expected = {"empire": {"id": "RmFjdGlvbjoy", "name": "Galactic Empire"}}
    result = await graphql(StarWarsSchema, query)
    assert result == (expected, None)


@mark.asyncio
async def test_correctly_refetches_empire():
    query = """
      query EmpireRefetchQuery {
        node(id: "RmFjdGlvbjoy") {
          id
          ... on Faction {
            name
          }
        }
      }
    """
    expected = {"node": {"id": "RmFjdGlvbjoy", "name": "Galactic Empire"}}
    result = await graphql(StarWarsSchema, query)
    assert result == (expected, None)


@mark.asyncio
async def test_correctly_refetches_xwing():
    query = """
      query XWingRefetchQuery {
        node(id: "U2hpcDox") {
          id
          ... on Ship {
            name
          }
        }
      }
    """
    expected = {"node": {"id": "U2hpcDox", "name": "X-Wing"}}
    result = await graphql(StarWarsSchema, query)
    assert result == (expected, None)
